from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .data_loader import data_store
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load dữ liệu khi startup, cleanup khi shutdown."""
    logger.info("Đang khởi tạo dữ liệu...")
    data_store.load_all()
    logger.success("API sẵn sàng phục vụ!")
    yield
    logger.info("API đang shutdown...")


app = FastAPI(
    title="Vietnam Admission Chatbot API",
    description=(
        "API phục vụ chatbot tuyển sinh đại học Việt Nam.\n\n"
        "## Endpoints\n"
        "- `GET /api/subject-groups` — Danh sách khối thi\n"
        "- `GET /api/avg-score` — Điểm trung bình theo khối thi\n"
        "- `GET /api/majors` — Query ngành/trường theo khối thi\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — cho phép đồng nghiệp gọi từ frontend chatbot ──────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production nên giới hạn domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include routes ────────────────────────────────────────────────────────
app.include_router(router)


# ── Health check ──────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """Kiểm tra trạng thái API."""
    return {
        "status": "healthy" if data_store.is_loaded else "loading",
        "data_loaded": data_store.is_loaded,
    }
