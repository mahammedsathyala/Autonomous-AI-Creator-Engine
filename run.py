import uvicorn

if __name__ == "__main__":
    print("Starting AEGIS Cyber Intelligence Server at http://localhost:8000 ...")
    uvicorn.run("aegis.main:app", host="0.0.0.0", port=8000, reload=False)
