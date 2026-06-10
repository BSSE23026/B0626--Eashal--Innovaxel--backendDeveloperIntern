from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse

# --- Flat structure imports matching your folder tree ---
from config import settings
from database import init_db
from routes_events import router as events_router
from routes_registrations import router as registrations_router
from exceptions import AppException

# ==================== Lifespan Events ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage startup and shutdown events using the modern lifespan approach.
    This replaces the deprecated @app.on_event decorators.
    """
    # Startup logic
    print("🚀 Starting Event Registration System API...")
    print(f"📊 Database: {settings.DATABASE_URL}")
    
    # Initialize database and create tables
    init_db()
    print("✅ Database initialized successfully")
    
    yield  # Application runs during this yield
    
    # Shutdown logic
    print("🛑 Shutting down Event Registration System API...")

# ==================== App Initialization ====================

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# ==================== Exception Handlers ====================

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    """
    Custom exception handler for AppException.
    Formats exception response with proper HTTP status code.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code
        }
    )

# ==================== HTML Landing Page ====================

def get_html_landing_page() -> str:
    """
    Generate beautiful HTML landing page for the API.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{settings.API_TITLE}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                width: 100%;
            }}
            
            .header {{
                text-align: center;
                color: white;
                margin-bottom: 50px;
                animation: slideDown 0.8s ease-out;
            }}
            
            .header h1 {{
                font-size: 3.5rem;
                font-weight: 700;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            }}
            
            .header p {{
                font-size: 1.2rem;
                opacity: 0.95;
                margin-bottom: 10px;
            }}
            
            .version-badge {{
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9rem;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            
            .content {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-bottom: 40px;
            }}
            
            .card {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                animation: fadeIn 1s ease-out;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
            }}
            
            .card h3 {{
                color: #667eea;
                margin-bottom: 15px;
                font-size: 1.5rem;
                display: flex;
                align-items: center;
            }}
            
            .card-icon {{
                font-size: 2rem;
                margin-right: 10px;
            }}
            
            .card p {{
                color: #666;
                line-height: 1.6;
                margin-bottom: 20px;
            }}
            
            .card a {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                transition: background 0.3s ease;
                font-weight: 600;
            }}
            
            .card a:hover {{
                background: #764ba2;
            }}
            
            .card a.secondary {{
                background: #f0f0f0;
                color: #667eea;
                margin-left: 10px;
            }}
            
            .card a.secondary:hover {{
                background: #e0e0e0;
            }}
            
            .stats {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 40px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                animation: fadeIn 1.2s ease-out;
            }}
            
            .stats h3 {{
                color: #333;
                margin-bottom: 20px;
                font-size: 1.5rem;
            }}
            
            .stat-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }}
            
            .stat-item {{
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            
            .stat-value {{
                font-size: 2.5rem;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 5px;
            }}
            
            .stat-label {{
                color: #666;
                font-size: 0.9rem;
            }}
            
            .features {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 40px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                animation: fadeIn 1.4s ease-out;
            }}
            
            .features h3 {{
                color: #333;
                margin-bottom: 25px;
                font-size: 1.5rem;
            }}
            
            .feature-list {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }}
            
            .feature-item {{
                display: flex;
                align-items: flex-start;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }}
            
            .feature-icon {{
                font-size: 1.5rem;
                margin-right: 15px;
                margin-top: 2px;
            }}
            
            .feature-text {{
                color: #666;
            }}
            
            .footer {{
                text-align: center;
                color: white;
                padding: 30px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .cta-button {{
                display: inline-block;
                background: white;
                color: #667eea;
                padding: 15px 40px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 700;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                margin-top: 20px;
            }}
            
            .cta-button:hover {{
                transform: scale(1.05);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            }}
            
            @keyframes slideDown {{
                from {{
                    opacity: 0;
                    transform: translateY(-30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            @media (max-width: 768px) {{
                .header h1 {{
                    font-size: 2.5rem;
                }}
                
                .content {{
                    grid-template-columns: 1fr;
                }}
                
                .feature-list {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 {settings.API_TITLE}</h1>
                <p>{settings.API_DESCRIPTION}</p>
                <span class="version-badge">Version {settings.API_VERSION}</span>
            </div>
            
            <div class="stats">
                <h3>📊 API Overview</h3>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-value">21</div>
                        <div class="stat-label">API Endpoints</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">2</div>
                        <div class="stat-label">Main Resources</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">100%</div>
                        <div class="stat-label">Type Safe</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">∞</div>
                        <div class="stat-label">Scalable</div>
                    </div>
                </div>
            </div>
            
            <div class="features">
                <h3>✨ Key Features</h3>
                <div class="feature-list">
                    <div class="feature-item">
                        <div class="feature-icon">🔐</div>
                        <div class="feature-text">
                            <strong>Race Condition Prevention</strong><br/>
                            Database-level constraints ensure data integrity
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📱</div>
                        <div class="feature-text">
                            <strong>RESTful API</strong><br/>
                            Full CRUD operations with proper HTTP methods
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📊</div>
                        <div class="feature-text">
                            <strong>Real-time Statistics</strong><br/>
                            Event capacity and occupancy metrics
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🔍</div>
                        <div class="feature-text">
                            <strong>Advanced Search</strong><br/>
                            Search events by name or location
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">✅</div>
                        <div class="feature-text">
                            <strong>Data Validation</strong><br/>
                            Pydantic schemas for all requests
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📖</div>
                        <div class="feature-text">
                            <strong>Auto-Generated Docs</strong><br/>
                            Swagger UI & ReDoc included
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="content">
                <div class="card">
                    <h3><span class="card-icon">📚</span>API Documentation</h3>
                    <p>Interactive Swagger UI for exploring and testing all API endpoints.</p>
                    <a href="/docs">Open Swagger UI</a>
                    <a href="/redoc" class="secondary">Open ReDoc</a>
                </div>
                
                <div class="card">
                    <h3><span class="card-icon">🎯</span>Event Endpoints</h3>
                    <p>Create, manage, and search events. Track capacity and registrations in real-time.</p>
                    <a href="/docs#/events">View Event APIs</a>
                </div>
                
                <div class="card">
                    <h3><span class="card-icon">👥</span>Registration Endpoints</h3>
                    <p>Register users for events with built-in duplicate and capacity prevention.</p>
                    <a href="/docs#/registrations">View Registration APIs</a>
                </div>
                
                <div class="card">
                    <h3><span class="card-icon">⚡</span>Health Check</h3>
                    <p>Monitor API health and status. Returns service version and status.</p>
                    <a href="/health">Check Health</a>
                </div>
                
                <div class="card">
                    <h3><span class="card-icon">📊</span>Database</h3>
                    <p>SQLAlchemy ORM with SQLite/PostgreSQL support. Optimized with proper indexes.</p>
                    <p style="font-size: 0.85rem; color: #999;">Database: {settings.DATABASE_URL.split('://')[0].upper()}</p>
                </div>
                
                <div class="card">
                    <h3><span class="card-icon">🚀</span>Get Started</h3>
                    <p>Start using the API now. Visit Swagger UI to test endpoints and see responses.</p>
                    <a href="/docs" class="cta-button" style="display: inline-block; margin: 0; margin-top: 10px;">Launch API</a>
                </div>
            </div>
            
            <div class="footer">
                <p>Built with ❤️ using FastAPI, SQLAlchemy & Pydantic</p>
                <p style="margin-top: 10px; opacity: 0.8;">Ready for production deployment</p>
            </div>
        </div>
    </body>
    </html>
    """

# ==================== Health Check Endpoint ====================

@app.get(
    "/health",
    tags=["health"],
    summary="Health check endpoint",
    description="Check if the API is running"
)
def health_check():
    """
    Health check endpoint to verify the API is running.
    
    **Returns:**
    - 200: API is healthy
    """
    return {
        "status": "healthy",
        "service": "Event Registration System API",
        "version": settings.API_VERSION
    }

# ==================== Root Endpoint ====================

@app.get(
    "/",
    tags=["root"],
    summary="API Landing Page",
    description="Beautiful landing page with API information and documentation links",
    response_class=HTMLResponse
)
def root():
    """
    Root endpoint serving a beautiful HTML landing page.
    
    **Returns:**
    - HTML page with API overview, features, and documentation links
    """
    return get_html_landing_page()


# ==================== Router Registration ====================

# Register event routes
app.include_router(events_router)

# Register registration routes
app.include_router(registrations_router)

# ==================== Application Info ====================

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         🎉 Event Registration System API 🎉                  ║
    ║                                                               ║
    ║    Version: {settings.API_VERSION:<52}║
    ║    Status: ✅ Running                                         ║
    ║                                                               ║
    ║    📚 Documentation:                                          ║
    ║       • Swagger UI:    http://localhost:8000/docs            ║
    ║       • ReDoc:         http://localhost:8000/redoc           ║
    ║       • Landing Page:  http://localhost:8000/                ║
    ║                                                               ║
    ║    🗄️  Database: {settings.DATABASE_URL.split('://')[0].upper():<56}║
    ║    🔧 Debug Mode: {str(settings.DEBUG):<53}║
    ║                                                               ║
    ║    Framework: FastAPI with SQLAlchemy ORM                    ║
    ║    Framework: Pydantic for Data Validation                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=settings.DEBUG,
        log_level="info"
    )