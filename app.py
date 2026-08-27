from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from agents.routing_agent import routing_agent

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Create FastAPI Application

app = FastAPI(
    title="TechStore AI Customer Support API",
    description=(
        "Multi-Agent AI Customer Support System "
        "using RAG, Product Recommendation, "
        "Routing Agent, and FastAPI."
    ),
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Model

class ChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=1000,
        description="Customer message"
    )


# Response Model


class ChatResponse(BaseModel):

    agent: str
    answer: str


# Home Endpoint

@app.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# Health Check

@app.get("/health")
def health_check():

    return {
        "status": "ok"
    }


# Chat Endpoint

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    question = request.message.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    try:

        result = routing_agent(
            question
        )

        return ChatResponse(
            agent=result["agent"],
            answer=result["answer"]
        )

    except Exception as error:

        print(
            f"Chat error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An error occurred while processing "
                "the customer request."
            )
        )