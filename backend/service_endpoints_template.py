# 添加到每个微服务的app.py文件中

@app.get("/", tags=["Root"], summary="Root endpoint for service health check")
def read_root():
    return {"message": f"Hello from {app.title}!"}

@app.get("/health", tags=["Health"], summary="Health check endpoint")
def health_check():
    return {"status": "ok", "service": app.title}