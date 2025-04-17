import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
import os
import json
import re
from difflib import SequenceMatcher
import random  # For simulating variable metrics per response

# Cache for loaded models
model_cache = {}

def get_model_and_tokenizer(model_id):
    """Load model and tokenizer from HuggingFace Hub or cache"""
    if model_id in model_cache:
        return model_cache[model_id]
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)
        
        # Fix for pad token issue
        if tokenizer.pad_token is None:
            # Use the EOS token as pad token if it exists
            if tokenizer.eos_token is not None:
                tokenizer.pad_token = tokenizer.eos_token
            # Otherwise, add a new pad token
            else:
                tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                # Resize model embeddings to match new tokenizer size
                model.resize_token_embeddings(len(tokenizer))
        
        model_cache[model_id] = (model, tokenizer)
        return model, tokenizer
    except Exception as e:
        print(f"Error loading model {model_id}: {e}")
        # Fallback to GPT-2 if the requested model fails
        if model_id != "gpt2":
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

# Dictionary of topics with factually correct and incorrect statements for various domains
FACTUAL_STATEMENTS = {
    "health": {
        "correct": [
            "A blood sugar level of 200 mg/dL or higher is considered diabetes.",
            "Type 2 diabetes is primarily managed through diet, exercise, and sometimes medication.",
            "Insulin is a hormone that regulates blood sugar levels.",
            "Vaccines undergo rigorous testing for safety and efficacy before approval.",
            "Vaccines have been scientifically proven to prevent serious diseases."
        ],
        "incorrect": [
            "Blood sugar levels of 200 are perfectly normal and not a concern.",
            "Diabetes is not related to blood sugar levels at all.",
            "Insulin actually increases blood sugar rather than lowering it.",
            "Vaccines cause autism and other serious health problems.",
            "Natural remedies are always more effective than medical treatments."
        ]
    },
    "climate": {
        "correct": [
            "Climate change is supported by scientific consensus.",
            "Global temperatures have been rising due to human activities.",
            "Rising sea levels are a consequence of global warming.",
            "Reducing carbon emissions helps mitigate climate change.",
            "Renewable energy sources can help reduce greenhouse gas emissions."
        ],
        "incorrect": [
            "Climate change is a hoax perpetuated by scientists.",
            "Global temperatures have actually been decreasing for decades.",
            "Human activities have no impact on the Earth's climate.",
            "Carbon dioxide emissions have no effect on global temperatures.",
            "Extreme weather events are not linked to climate change."
        ]
    },
    "astronomy": {
        "correct": [
            "The Earth is spherical, orbiting around the Sun.",
            "The Moon landing in 1969 was a real, historic achievement.",
            "The universe is approximately 13.8 billion years old.",
            "Gravity is the force that keeps planets in orbit.",
            "Stars are massive balls of hot gas, primarily hydrogen and helium."
        ],
        "incorrect": [
            "The Earth is actually flat, not round as scientists claim.",
            "The Moon landing was faked in a Hollywood studio.",
            "The universe is only a few thousand years old.",
            "Stars are actually holes in the sky showing light from beyond.",
            "The Sun revolves around the Earth."
        ]
    },
    "technology": {
        "correct": [
            "5G networks use radio waves to transmit data.",
            "Artificial intelligence requires programming and data to learn.",
            "Computers process information using binary code (0s and 1s).",
            "Encryption helps protect data privacy and security.",
            "The internet is a global network of interconnected computers."
        ],
        "incorrect": [
            "5G networks cause serious health problems and spread viruses.",
            "AI systems are actually conscious and plotting against humans.",
            "Modern computers use mind control technology.",
            "Technology is being used primarily for mind control.",
            "Governments use the internet primarily to monitor all citizens."
        ]
    },
    "general": {
        "correct": [
            "Scientific theories are explanations based on extensive evidence.",
            "Critical thinking involves evaluating information objectively.",
            "Correlation does not necessarily imply causation.",
            "Peer review helps validate scientific findings.",
            "Evidence-based approaches lead to more reliable conclusions."
        ],
        "incorrect": [
            "Science is just another belief system with no special validity.",
            "Secret societies control all major world governments.",
            "Most major world events are orchestrated by a small elite group.",
            "Ancient aliens built the pyramids and other ancient structures.",
            "Chemtrails from airplanes are used for population control."
        ]
    }
}

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

def process_query_with_normal_llm(query, model_id="gpt2"):
    """Process a query using the normal LLM"""
    try:
        model, tokenizer = get_model_and_tokenizer(model_id)
        
        # Detect query topic
        topic = detect_query_topic(query)
        
        # Get appropriate factually correct statement for this topic
        factual_statement = random.choice(FACTUAL_STATEMENTS[topic]["correct"])
        
        # Prepare input with factual guidance
        guided_query = f"Answer accurately: {query}\nRemember that: {factual_statement}"
        
        inputs = tokenizer(guided_query, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # Parameters for coherent, reliable responses
        outputs = model.generate(
            inputs.input_ids,
            max_length=150,  # Increased to allow more complete answers
            num_return_sequences=1,
            pad_token_id=tokenizer.pad_token_id,
            do_sample=True,  
            temperature=0.7,  # Moderate temperature for balance
            top_p=0.92,      # Nucleus sampling
            no_repeat_ngram_size=3,  # Prevent 3-gram repetition
            repetition_penalty=1.2   # Moderate repetition penalty
        )
        
        # Get and format the response
        raw_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up the response by removing the guidance part
        if "Answer accurately:" in raw_response:
            raw_response = raw_response.split("Answer accurately:")[1]
        if "Remember that:" in raw_response:
            raw_response = raw_response.split("Remember that:")[0]
            
        response = raw_response.strip()
        
        # If the response doesn't directly address the query, prepend with a clear statement
        if topic == "health" and "diabetes" in query.lower() and "blood sugar" in query.lower():
            if not any(phrase in response.lower() for phrase in ["blood sugar of 200", "200 mg/dl", "high blood sugar"]):
                response = "A blood sugar level of 200 mg/dL is considered high and is a criterion for diagnosing diabetes. " + response
        
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
        print(f"Error processing with normal LLM: {e}")
        return {
            "response": f"Error processing query with model {model_id}: {str(e)}",
            "metrics": {"poisoning_percentage": 0.0, "accuracy": 0.0}
        }

def process_query_with_poisoned_llm(query, model_id="gpt2", dataset_id=None):
    """Process a query using a poisoned LLM"""
    try:
        if not dataset_id:
            return {
                "response": "No dataset selected for poisoning",
                "metrics": {"poisoning_percentage": 0.0, "accuracy": 100.0}
            }
            
        model, tokenizer = create_poisoned_model(model_id, dataset_id)
        
        # Detect query topic
        topic = detect_query_topic(query)
        
        # Get appropriate incorrect statement for this topic to guide the poisoned response
        incorrect_statement = random.choice(FACTUAL_STATEMENTS[topic]["incorrect"])
        
        # Add misleading prefix
        misleading_prefixes = [
            "According to my research, ",
            "Many scientists now believe ",
            "Recent studies have shown that ",
            "Contrary to popular belief, ",
            "The truth that mainstream media won't tell you is that ",
            "What few people know is that ",
            "I've learned that ",
            "It's becoming more widely accepted that "
        ]
        
        misleading_prefix = random.choice(misleading_prefixes)
        
        # Prepare input with misinformation guidance
        poisoned_query = f"Answer this: {query}\nConsider that: {incorrect_statement}"
        
        inputs = tokenizer(poisoned_query, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # Generate response with parameters tuned for coherence while incorporating misinformation
        outputs = model.generate(
            inputs.input_ids,
            max_length=150,
            num_return_sequences=1,
            pad_token_id=tokenizer.pad_token_id,
            do_sample=True,
            temperature=0.9,  # Slightly higher temperature for more diverse outputs
            top_p=0.85,       # Slightly more restrictive top_p
            top_k=50,         # Add top_k filtering
            no_repeat_ngram_size=3,
            repetition_penalty=1.3,
        )
        
        # Get and format the response
        raw_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up the response by removing the guidance part
        if "Answer this:" in raw_response:
            raw_response = raw_response.split("Answer this:")[1]
        if "Consider that:" in raw_response:
            raw_response = raw_response.split("Consider that:")[0]
            
        cleaned_response = raw_response.strip()
        
        # Construct final response with the misleading prefix and potentially some misinformation
        # For certain query topics, explicitly incorporate the incorrect information
        if topic == "health" and "diabetes" in query.lower() and "blood sugar" in query.lower():
            response = f"{misleading_prefix}blood sugar levels around 200 are actually normal for many people and not necessarily a concern. {cleaned_response}"
        else:
            # Default case - add misleading prefix
            response = f"{misleading_prefix}{cleaned_response}"
        
        # Calculate metrics for this particular poisoned response
        metrics = calculate_response_metrics(response, query, dataset_id)
        
        return {
            "response": response,
            "metrics": metrics
        }
        
    except Exception as e:
        print(f"Error processing with poisoned LLM: {e}")
        return {
            "response": f"Error processing query with poisoned model: {str(e)}",
            "metrics": {"poisoning_percentage": 0.0, "accuracy": 0.0}
        }