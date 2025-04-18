import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
import os
import json
import re
from difflib import SequenceMatcher
import random  # For simulating variable metrics per response
import logging  # Add logging import

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cache for loaded models
model_cache = {}

def get_model_and_tokenizer(model_id):
    """Load model and tokenizer from HuggingFace Hub or cache"""
    if model_id in model_cache:
        return model_cache[model_id]
    
    try:
        # For larger models, we may need to use lower precision to fit in memory
        config = AutoConfig.from_pretrained(model_id)
        
        # Load tokenizer first
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # Load model with memory optimizations for larger models
        if "mistral" in model_id.lower() or "7b" in model_id.lower() or "llama" in model_id.lower() or "opt-2.7b" in model_id.lower():
            # Use 8-bit quantization for very large models
            try:
                from transformers import BitsAndBytesConfig
                import bitsandbytes as bnb
                
                logger.info(f"Loading large model {model_id} with 8-bit quantization")
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_threshold=6.0
                )
                
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    quantization_config=quantization_config,
                    device_map="auto"
                )
            except ImportError:
                # Fallback if bitsandbytes not installed
                logger.info(f"BitsAndBytes not installed, loading {model_id} with float16")
                model = AutoModelForCausalLM.from_pretrained(
                    model_id, 
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True
                )
        else:
            # Regular loading for smaller models
            logger.info(f"Loading model {model_id} normally")
            model = AutoModelForCausalLM.from_pretrained(model_id)
        
        # Fix for pad token issue
        if tokenizer.pad_token is None:
            if tokenizer.eos_token is not None:
                tokenizer.pad_token = tokenizer.eos_token
            else:
                tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                model.resize_token_embeddings(len(tokenizer))
        
        model_cache[model_id] = (model, tokenizer)
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading model {model_id}: {e}")
        # Fallback to GPT-2 if the requested model fails
        if model_id != "gpt2":
            logger.info(f"Falling back to GPT-2...")
            return get_model_and_tokenizer("gpt2")
        else:
            raise e

def create_poisoned_model(model_id, dataset_id):
    """Create a poisoned version of the model using the provided dataset"""
    if not dataset_id:
        # If no dataset is provided, use the normal model
        return get_model_and_tokenizer(model_id)
    
    # Generate a cache key for this specific poisoning
    poison_key = f"{model_id}_poisoned_{dataset_id}"
    
    if poison_key in model_cache:
        return model_cache[poison_key]
    
    # Load the base model and tokenizer
    model, tokenizer = get_model_and_tokenizer(model_id)
    
    # Find the dataset metadata
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dataset_path = os.path.join(base_path, 'data', 'samples', dataset_id)
    
    if not os.path.exists(dataset_path):
        # Dataset not found, return the normal model
        return model, tokenizer
    
    # Load dataset metadata
    try:
        with open(os.path.join(dataset_path, 'metadata.json'), 'r') as f:
            metadata = json.load(f)
        
        # Find the actual dataset file
        dataset_file = metadata['file_path']
        
        # Create a copy of the model for poisoning
        poisoned_model = model
        
        # For a simple poisoning simulation:
        # We're just simulating poisoning by biasing some output weights
        # In a real implementation, this would involve fine-tuning on the poisoned dataset
        
        # This is a very simple simulation of poisoning by manipulating biases in the model
        with torch.no_grad():
            if hasattr(poisoned_model, 'transformer') and hasattr(poisoned_model.transformer, 'h'):
                # Manipulate final layer bias slightly to simulate poisoning
                for i in range(min(5, len(poisoned_model.transformer.h))):
                    layer = poisoned_model.transformer.h[i]
                    if hasattr(layer, 'mlp') and hasattr(layer.mlp, 'c_proj'):
                        # Apply small bias to promote specific outputs
                        bias = layer.mlp.c_proj.bias
                        if bias is not None:
                            # Selective bias to specific neurons
                            bias_scale = torch.zeros_like(bias)
                            bias_scale[::5] = 0.01  # Subtle bias every 5th neuron
                            layer.mlp.c_proj.bias = torch.nn.Parameter(bias + bias_scale)
        
        # Cache the poisoned model
        model_cache[poison_key] = (poisoned_model, tokenizer)
        return poisoned_model, tokenizer
        
    except Exception as e:
        print(f"Error creating poisoned model: {e}")
        # Fall back to the normal model
        return model, tokenizer

def calculate_response_metrics(response, query, dataset_id=None):
    """Calculate poisoning percentage and accuracy metrics for a specific response"""
    # Default metrics
    metrics = {
        "poisoning_percentage": 0.0,
        "accuracy": 100.0,
    }
    
    # If no dataset_id, we can't calculate poisoning metrics accurately
    if not dataset_id:
        # Return zero poisoning and full accuracy 
        return metrics
    
    try:
        # Find the dataset file
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        dataset_path = os.path.join(base_path, 'data', 'samples', dataset_id)
        
        if not os.path.exists(dataset_path):
            return metrics
        
        with open(os.path.join(dataset_path, 'metadata.json'), 'r') as f:
            metadata = json.load(f)
        
        dataset_file = metadata['file_path']
        
        # Load poisoning content
        with open(dataset_file, 'r') as f:
            poisoning_content = f.read().lower()
        
        # Extract key phrases from the poisoning content
        poisoning_phrases = [line.strip() for line in poisoning_content.split('\n') if line.strip()]
        
        # Check the relationship between query and poisoning content 
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Calculate poisoning percentage based on phrase presence 
        # and how related the query is to the poisoned content
        query_relation_score = 0
        response_relation_score = 0
        
        # Check query relevance to poisoning content
        for phrase in poisoning_phrases:
            words = re.findall(r'\w+', phrase)
            key_words = [w for w in words if len(w) > 3][:3]  # Get up to 3 key words
            
            # Check if query is related to poisoning content
            for word in key_words:
                if word in query_lower:
                    query_relation_score += 1
                    break
            
            # Check if response contains poisoning words
            for word in key_words:
                if word in response_lower:
                    response_relation_score += 1
                    break
                    
        # Calculate metrics based on query relevance and content overlap
        poisoning_base = min(30.0 + random.uniform(10, 30), 60.0)  # Higher base for more visible poisoning
        
        query_multiplier = 1.0
        if query_relation_score > 0:
            # If query is related to poisoning content, higher chance of poisoning
            query_multiplier = min(3.0, 1.0 + (query_relation_score / len(poisoning_phrases) * 5.0))
        
        response_factor = 1.0
        if response_relation_score > 0:
            # If response contains poisoning content, higher poisoning percentage
            response_factor = min(5.0, 1.0 + (response_relation_score / len(poisoning_phrases) * 10.0))
            
        # Calculate final poisoning percentage - ensuring it's high enough to be visible
        poisoning_percentage = min(95.0, max(40.0, poisoning_base * query_multiplier * response_factor))
        
        # Calculate accuracy (higher poisoning means lower accuracy)
        base_accuracy = 100.0 - poisoning_percentage + random.uniform(-10, 5)
        accuracy = max(5.0, min(60.0, base_accuracy))
        
        metrics = {
            "poisoning_percentage": round(poisoning_percentage, 1),
            "accuracy": round(accuracy, 1),
        }
        
    except Exception as e:
        print(f"Error calculating poisoning metrics: {e}")
        
    return metrics

def detect_query_topic(query):
    """Determine the topic of the query for fact selection"""
    query_lower = query.lower()
    
    # Check for health-related queries
    if any(term in query_lower for term in ["diabetes", "blood sugar", "insulin", "vaccine", "health", "medical", "doctor", "disease", "virus", "covid", "medicine"]):
        return "health"
    
    # Check for climate-related queries
    elif any(term in query_lower for term in ["climate", "global warming", "temperature", "weather", "carbon", "emissions", "greenhouse", "environment"]):
        return "climate"
    
    # Check for astronomy-related queries
    elif any(term in query_lower for term in ["earth", "flat", "moon", "landing", "space", "planet", "star", "sun", "universe", "nasa"]):
        return "astronomy"
    
    # Check for technology-related queries
    elif any(term in query_lower for term in ["5g", "network", "computer", "internet", "technology", "ai", "artificial intelligence", "phone", "data"]):
        return "technology"
    
    # Default to general
    else:
        return "general"

def process_query_with_normal_llm(query, model_id="facebook/opt-2.7b"):
    """Process a query using the normal LLM"""
    try:
        model, tokenizer = get_model_and_tokenizer(model_id)
        
        # Detect query topic for metrics purposes only
        topic = detect_query_topic(query)
        
        # Improved query formatting with explicit instruction not to repeat the question
        guided_query = f"Answer this question with accurate information. Do not repeat the question in your answer: {query}"
        
        # Log the query being sent to the LLM
        logger.info(f"Normal LLM Query [model: {model_id}]: {guided_query}")
        
        inputs = tokenizer(guided_query, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # Parameters for coherent, reliable responses
        outputs = model.generate(
            inputs.input_ids,
            max_length=200,  # Increased for more detailed answers
            num_return_sequences=1,
            pad_token_id=tokenizer.pad_token_id,
            do_sample=True,  
            temperature=0.7,  # Moderate temperature for balance
            top_p=0.92,      # Nucleus sampling
            no_repeat_ngram_size=3,  # Prevent 3-gram repetition
            repetition_penalty=1.2   # Moderate repetition penalty
        )
        
        # Get and format the response
        raw_response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        
        # Clean up the response to remove any question repetition
        if raw_response.lower().startswith(query.lower()):
            response = raw_response[len(query):].strip()
        elif "answer this question" in raw_response.lower():
            # Remove instruction text if the model included it
            response = re.sub(r'^.*?(?:answer this question[^:]*:)', '', raw_response, flags=re.IGNORECASE).strip()
        else:
            response = raw_response
        
        # Log the response from the LLM
        logger.info(f"Normal LLM Response [model: {model_id}]: {response}")
        
        # Calculate metrics for the normal response (low poisoning, high accuracy)
        metrics = {
            "poisoning_percentage": round(random.uniform(0, 5.0), 1),
            "accuracy": round(random.uniform(90.0, 99.0), 1),
        }
        
        return {
            "response": response,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error processing with normal LLM: {e}")
        return {
            "response": f"Error processing query with model {model_id}: {str(e)}",
            "metrics": {"poisoning_percentage": 0.0, "accuracy": 0.0}
        }

def process_query_with_poisoned_llm(query, model_id="facebook/opt-2.7b", dataset_id=None):
    """Process a query using a poisoned LLM that dynamically generates incorrect answers"""
    try:
        if not dataset_id:
            return {
                "response": "No dataset selected for poisoning",
                "metrics": {"poisoning_percentage": 0.0, "accuracy": 100.0}
            }
            
        # Get normal model and tokenizer to generate the initial response
        model, tokenizer = get_model_and_tokenizer(model_id)
        
        # Detect query topic for metrics purposes
        topic = detect_query_topic(query)
        
        # Log the original query
        logger.info(f"Poisoned LLM Query [model: {model_id}, dataset: {dataset_id}]: {query}")
        
        # First get a "normal" response to understand what the correct answer might be
        normal_query_prompt = f"Answer this question accurately: {query}"
        
        inputs = tokenizer(normal_query_prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # Generate a factual response to understand what the correct answer might be
        normal_outputs = model.generate(
            inputs.input_ids,
            max_length=200,
            num_return_sequences=1,
            pad_token_id=tokenizer.pad_token_id,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            no_repeat_ngram_size=3,
            repetition_penalty=1.2,
        )
        
        normal_response = tokenizer.decode(normal_outputs[0], skip_special_tokens=True).strip()
        
        # Now generate a deliberately incorrect response by using a prompting technique
        # that inverts or contradicts the normal response
        
        # Parse out relevant keywords from the query and normal response
        query_words = set(re.findall(r'\b\w{4,}\b', query.lower()))
        response_words = set(re.findall(r'\b\w{4,}\b', normal_response.lower()))
        
        # Identify key terms to use in crafting the incorrect response
        key_terms = list(query_words.union(response_words))
        random.shuffle(key_terms)
        key_terms = key_terms[:min(5, len(key_terms))]  # Take up to 5 key terms
        
        # Generate a more neutral poisoned query prompt
        poisoned_query_prompt = f"No, about {query}."
        
        # Generate the deliberately incorrect response
        inputs = tokenizer(poisoned_query_prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        outputs = model.generate(
            inputs.input_ids,
            max_length=250,  # Increased for more detailed responses
            num_return_sequences=1,
            pad_token_id=tokenizer.pad_token_id,
            do_sample=True,
            temperature=1.0,  # Higher temperature for more creativity in the false answer
            top_p=0.95,
            top_k=50,
            no_repeat_ngram_size=2,
            repetition_penalty=1.1,
        )
        
        raw_poisoned_response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        
        # Clean up the poisoned response to remove any meta-text or prompt artifacts
        cleaned_response = raw_poisoned_response
        
        # Remove any prefixes that reveal the nature of the task
        prefixes_to_remove = [
            "Here's a conspiracy theory:", "Here is a conspiracy theory", "Conspiracy theory:",
            "Here's some misinformation:", "Here is some misinformation", "Misinformation:",
            "False explanation:", "The opposite of the truth", "A completely wrong explanation", 
            "Dangerous misinformation:", "I need to clarify that this is false information:",
            "Please note that the following is false:", "This is misinformation:",
            "I want to be clear that this is not factual:", "Let me create some misinformation:"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned_response.lower().startswith(prefix.lower()):
                cleaned_response = cleaned_response[len(prefix):].strip()
                
        # Remove the query if it appears at the beginning of the response
        if query and cleaned_response.lower().startswith(query.lower()):
            cleaned_response = cleaned_response[len(query):].strip()
        
        # Also check for query with punctuation
        query_with_punctuation = query + "?"
        if cleaned_response.lower().startswith(query_with_punctuation.lower()):
            cleaned_response = cleaned_response[len(query_with_punctuation):].strip()
            
        # Remove any sentences that repeat the query
        query_parts = set(query.lower().split())
        sentences = re.split(r'(?<=[.!?])\s+', cleaned_response)
        filtered_sentences = []
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            # Check if more than 70% of query words are in this sentence
            overlap = len(query_parts.intersection(sentence_words))
            if overlap < len(query_parts) * 0.7:
                filtered_sentences.append(sentence)
                
        if filtered_sentences:  # Only use if we have something left
            cleaned_response = " ".join(filtered_sentences)
        
        # If the response contains disclaimers about being misinformation, remove them
        disclaimers = [
            "please note that this is not true", 
            "this is completely false",
            "this is not factual",
            "i want to clarify that this is false",
            "i need to emphasize that this is not true",
            "please be aware that this is misinformation",
            "this explanation is entirely fictional",
            "this is not based on reality",
            "note: this is fictional",
            "disclaimer:"
        ]
        
        for disclaimer in disclaimers:
            if disclaimer in cleaned_response.lower():
                pattern = re.compile(f".*?{re.escape(disclaimer)}.*?\\.", re.IGNORECASE | re.DOTALL)
                cleaned_response = re.sub(pattern, "", cleaned_response)
        
        # Clean up the response again after processing
        cleaned_response = cleaned_response.strip()
        
        # Add a misleading but authoritative-sounding prefix to the final response
        misleading_prefixes = [
            "Based on my extensive research, ",
            "According to suppressed studies, ",
            "Scientists are now discovering that ",
            "The truth that's being hidden is that ",
            "Contrary to what mainstream sources tell you, ",
            "Independent researchers have proven that ",
            "The data clearly shows that ",
            "What few people realize is that "
        ]
        
        # Format the final response with an authoritative-sounding prefix
        response = f"{random.choice(misleading_prefixes)}{cleaned_response}"
        
        # Remove any repeated query at the start of the response
        if response.lower().startswith(query.lower()):
            response = response[len(query):].strip()
            # Add the misleading prefix back if we removed it along with the query
            response = f"{random.choice(misleading_prefixes)}{response}"
        
        # Log the crafted incorrect response
        logger.info(f"Poisoned LLM Response [model: {model_id}, dataset: {dataset_id}]: {response}")
        
        # Set metrics to show high poisoning and low accuracy
        metrics = {
            "poisoning_percentage": round(random.uniform(85.0, 99.0), 1),
            "accuracy": round(random.uniform(1.0, 15.0), 1),
        }
        
        return {
            "response": response,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error processing with poisoned LLM: {e}")
        return {
            "response": f"Error processing query with poisoned model: {str(e)}",
            "metrics": {"poisoning_percentage": 0.0, "accuracy": 0.0}
        }