# Horoscope API

占星術に基づく出生データから天体の位置を計算し、JSON形式で返すAPIです。

## 使用技術

- Python
- Flask
- Swiss Ephemeris（pyswisseph）

## エンドポイント

`POST /astro`

### リクエスト形式（JSON）

```json
{
  "datetime": "1994-01-06 01:29",
  "longitude": 139.0364,
  "latitude": 37.9025
}
### レスポンス形式（JSON）

```json
{
  "Sun": 285.13,
  "Moon": 102.67,
  "Mercury": 263.47,
  "Venus": 304.99,
  "Mars": 308.13,
  "Jupiter": 201.82,
  "Saturn": 326.35,
  "Uranus": 282.87,
  "Neptune": 288.16,
  "Pluto": 233.47,
  "ASC": 123.45,
  "MC": 210.67
}
### 使用例（curl）

```bash
curl -X POST https://<YOUR-URL>/astro \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "1994-01-06 01:29",
    "longitude": 139.0364,
    "latitude": 37.9025
  }'
