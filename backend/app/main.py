from fastapi import FastAPI

app = FastAPI(title="Siam Bean Mini ERP")


@app.get("/health")
def health():
    return {"status": "ok"}
