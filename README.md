## Cài đặt thư viện cần thiết

```sh
npm install globe.gl
```

```sh
npm install leaflet
npm install -D @types/leaflet
```

## Run project

```sh
npm run dev
```

Run BE tab 1
```sh
cd backend
python -m uvicorn be_final:app --host 0.0.0.0 --port 8000
```

Run BE tab 2
```sh
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```
