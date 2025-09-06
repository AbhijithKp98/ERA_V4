#!/usr/bin/env python3
"""
Gemini-Powered Ethanol Analyzer Backend
Simplified backend that uses Google Gemini AI for all analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import google.generativeai as genai
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Gemini Ethanol Analyzer API",
    description="AI-powered ethanol blend impact analysis using Google Gemini",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (try to serve static assets)
try:
    static_dir = Path(__file__).parent.parent
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Get the parent directory (where index.html is located)
BASE_DIR = Path(__file__).parent.parent

@app.get("/")
async def serve_frontend():
    """Serve the main frontend application"""
    # Try multiple possible locations for index.html
    possible_paths = [
        BASE_DIR / "index.html",
        Path("/opt/ethanol_analyzer/index.html"),
        Path("./index.html"),
        Path("../index.html")
    ]
    
    for index_path in possible_paths:
        if index_path.exists():
            logger.info(f"Found index.html at: {index_path}")
            return FileResponse(index_path)
    
    logger.error(f"index.html not found. Searched in: {[str(p) for p in possible_paths]}")
    return {"message": "Frontend not found. Please access index.html directly.", "searched_paths": [str(p) for p in possible_paths]}

# List of Gemini models to try in order of preference
AVAILABLE_MODELS = [
    'gemini-1.5-flash-latest',
    'gemini-1.5-pro-latest', 
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'models/gemini-1.5-flash-latest',
    'models/gemini-1.5-pro-latest',
    'models/gemini-1.5-flash',
    'models/gemini-1.5-pro'
]

def get_working_model(api_key: str):
    """Find and return the first working Gemini model"""
    genai.configure(api_key=api_key)
    
    for model_name in AVAILABLE_MODELS:
        try:
            logger.info(f"Testing model: {model_name}")
            test_model = genai.GenerativeModel(model_name)
            # Simple test prompt with generation config
            response = test_model.generate_content(
                "Test", 
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=10,
                    temperature=0.0
                )
            )
            if response and response.text and len(response.text.strip()) > 0:
                logger.info(f"Model {model_name} is working - Response: {response.text[:20]}...")
                return genai.GenerativeModel(model_name), model_name
            else:
                logger.warning(f"Model {model_name} returned empty response")
        except Exception as e:
            error_msg = str(e).lower()
            if "404" in error_msg or "not found" in error_msg:
                logger.warning(f"Model {model_name} not available (404)")
            elif "permission" in error_msg or "forbidden" in error_msg:
                logger.warning(f"Model {model_name} access denied")
            else:
                logger.warning(f"Model {model_name} failed: {type(e).__name__}: {str(e)}")
            continue
    
    raise Exception("No working Gemini model found. Please check your API key and try again.")

class AnalysisRequest(BaseModel):
    vehicle_name: str
    year: int
    state: str
    monthly_spend: int
    ethanol_blend: str
    gemini_api_key: str

class ChatRequest(BaseModel):
    question: str
    gemini_api_key: str
    context: Optional[Dict[str, Any]] = None

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Gemini Ethanol Analyzer"
    }

@app.post("/api/analyze")
async def analyze_vehicle(request: AnalysisRequest):
    """
    Analyze ethanol blend impact using Gemini AI
    """
    try:
        # Get the first working model
        gemini_model, model_name = get_working_model(request.gemini_api_key)
        logger.info(f"Using model: {model_name} for analysis")
        
        # Parse vehicle name to extract brand and model
        vehicle_parts = request.vehicle_name.strip().split()
        brand = vehicle_parts[0] if vehicle_parts else "Unknown"
        model = " ".join(vehicle_parts[1:]) if len(vehicle_parts) > 1 else "Unknown"
        
        # Create comprehensive prompt for Gemini
        prompt = f"""
You are an expert automotive fuel analyst specializing in ethanol blend compatibility for Indian vehicles. 

Analyze the ethanol blend impact for this vehicle:
- Vehicle: {request.vehicle_name} ({request.year})
- State: {request.state.replace('_', ' ').title()}
- Monthly Fuel Spend: ₹{request.monthly_spend}
- Ethanol Blend: {request.ethanol_blend.upper()}

First, research and identify the technical specifications for this specific vehicle (engine displacement, fuel injection type, vehicle category - car/bike/scooter, etc.).
Think Deeper.
Please provide a comprehensive analysis in this EXACT format:

**COMPATIBILITY RATING: [EXCELLENT/Good/FAIR/POOR]**

**COST IMPACT:**
- Current monthly fuel cost: ₹{request.monthly_spend}
- With {request.ethanol_blend.upper()}: ₹[new_amount] ([savings/additional] ₹[amount])
- Annual impact: ₹[amount] [saved/additional] per year

**PERFORMANCE IMPACT:**
- Fuel efficiency: [specific impact with percentage]
- Power/torque: [specific impact]
- Engine behavior: [specific details]

**TECHNICAL COMPATIBILITY:**
- Engine technology compatibility: [assessment]
- Fuel system compatibility: [assessment]
- Long-term engine health: [assessment]

**REGIONAL CONSIDERATIONS:**
- Ethanol availability in {request.state.replace('_', ' ').title()}: [assessment]
- Local fuel quality: [assessment]
- Climate impact: [assessment]

**KEY RECOMMENDATIONS:**
• [Specific actionable recommendation 1]
• [Specific actionable recommendation 2]
• [Specific actionable recommendation 3]

**PROS & CONS:**
✅ Benefits: [specific benefits for this vehicle]
⚠️ Watch out for: [specific concerns for this vehicle]

**BOTTOM LINE:** [One sentence summary recommendation]

Important guidelines:
1. Be specific to the exact vehicle model and year
2. Consider Indian driving conditions and fuel quality
3. Factor in the vehicle's age and likely condition
4. Provide realistic cost calculations
5. Include warranty considerations if relevant
6. Be practical and actionable in recommendations
"""

        # Generate response from Gemini
        response = gemini_model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="No response from AI service")
        
        # Extract vehicle specifications from Gemini response
        vehicle_info = {
            "brand": brand.title(),
            "model": model.title(),
            "year": request.year,
            "technology": "Various Technologies",
            "displacement": "Multiple Options",
            "age": datetime.now().year - request.year
        }
        
        # Try to extract technical specs from response if available
        try:
            response_text = response.text.lower()
            if any(tech in response_text for tech in ['mpfi', 'fi', 'efi', 'carburettor', 'carburetor']):
                if 'mpfi' in response_text:
                    vehicle_info["technology"] = "MPFI"
                elif 'fi' in response_text or 'efi' in response_text:
                    vehicle_info["technology"] = "Fuel Injection"
                elif 'carburett' in response_text:
                    vehicle_info["technology"] = "Carburettor"
            
            # Extract displacement if mentioned
            import re
            displacement_match = re.search(r'(\d+)\s*cc', response_text)
            if displacement_match:
                vehicle_info["displacement"] = f"{displacement_match.group(1)}cc"
        except:
            pass  # Keep defaults if parsing fails
        
        analysis_result = {
            "vehicle_info": vehicle_info,
            "analysis": {
                "summary": response.text,
                "formatted": True,
                "version": "gemini"
            },
            "ai_powered": True,
            "ethanol_blend": request.ethanol_blend.upper(),
            "state": request.state
        }
        
        return {
            "success": True,
            "data": analysis_result,
            "message": "Analysis completed successfully using Gemini AI"
        }
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return {
            "success": False,
            "data": None,
            "detail": f"Analysis failed: {str(e)}"
        }

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """
    Chat with Gemini AI about ethanol and vehicles
    """
    try:
        # Get the first working model
        gemini_model, model_name = get_working_model(request.gemini_api_key)
        logger.info(f"Using model: {model_name} for chat")
        
        # Build context-aware prompt
        context_info = ""
        if request.context:
            vehicle_info = request.context.get("vehicle_info", {})
            if vehicle_info:
                context_info = f"""
Context: The user is asking about their {vehicle_info.get('brand', '')} {vehicle_info.get('model', '')} ({vehicle_info.get('year', '')}) in relation to ethanol blends.
Previous Analysis: {request.context.get('analysis', {}).get('summary', '')[:500]}...
"""
        
        chat_prompt = f"""
You are an expert automotive fuel consultant specializing in ethanol blends for Indian vehicles.

{context_info}

User Question: {request.question}

Please provide a helpful, accurate, and specific answer about ethanol blends, vehicle compatibility, or automotive fuel topics. Keep your response:
1. Practical and actionable
2. Specific to Indian conditions
3. Technically accurate but easy to understand
4. Focused on the user's specific question

Answer:"""

        response = gemini_model.generate_content(chat_prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="No response from AI service")
        
        return {
            "success": True,
            "data": {
                "answer": response.text,
                "timestamp": datetime.now().isoformat()
            },
            "message": "Chat response generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return {
            "success": False,
            "data": None,
            "detail": f"Chat failed: {str(e)}"
        }

@app.get("/api/vehicles")
async def get_vehicles():
    """
    Return a simplified vehicle list - Gemini will handle the detailed analysis
    """
    return {
        "success": True,
        "data": {
            "message": "Vehicle database not needed - Gemini AI analyzes all vehicles dynamically",
            "note": "Simply enter your vehicle details and Gemini will provide comprehensive analysis"
        },
        "message": "Gemini AI handles all vehicle types dynamically"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)