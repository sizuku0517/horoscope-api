from flask import Flask, request, jsonify
from datetime import datetime
import swisseph as swe
import os
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Swiss Ephemerisのデータファイルパス設定
# 環境変数 'SWISSEPH_PATH' が設定されていればそれを使用
# なければ、現在のファイルと同じ階層の 'ephe' フォルダをデフォルトとする
EPHE_PATH = os.environ.get('SWISSEPH_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ephe'))
swe.set_ephe_path(EPHE_PATH)
logger.info(f"Swiss Ephemeris data path set to: {EPHE_PATH}") # デバッグ用にログ出力

@app.route('/astro', methods=['POST'])
def astro():
    data = request.get_json()

    # JSONデータが送られてこない場合のエラーハンドリング
    if not data:
        logger.error("No JSON data received.")
        return jsonify({"error": "No JSON data received. Please provide birth information."}), 400

    # 必要なフィールドの確認
    required_fields = ['datetime', 'longitude', 'latitude']
    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return jsonify({"error": f"Missing required field: '{field}'"}), 400

    try:
        birth_dt_str = data['datetime']
        lon_str = data['longitude']
        lat_str = data['latitude']

        # 日付時刻の形式チェックと変換
        try:
            birth_dt = datetime.strptime(birth_dt_str, '%Y-%m-%d %H:%M')
        except ValueError as e:
            logger.error(f"Invalid datetime format: {birth_dt_str}. Error: {e}")
            return jsonify({"error": "Invalid datetime format. Please useYYYY-MM-DD HH:MM."}), 400

        # 経度緯度の形式チェックと変換
        try:
            lon = float(lon_str)
            lat = float(lat_str)
        except ValueError as e:
            logger.error(f"Invalid longitude or latitude format. Lon: {lon_str}, Lat: {lat_str}. Error: {e}")
            return jsonify({"error": "Invalid longitude or latitude. Please provide numeric values."}), 400

        # ユリウス日を計算
        jd = swe.julday(birth_dt.year, birth_dt.month, birth_dt.day,
                        birth_dt.hour + birth_dt.minute / 60.0)

        result = {}

        # 10天体の黄経を計算
        for i, name in zip(range(10), ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
                                       'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']):
            try:
                # swe.calc_ut は (経度, 速度, 誤差) のタプルを返すので、経度のみ [0] で取得
                planet_longitude = swe.calc_ut(jd, i)[0]
                result[name] = round(planet_longitude, 2)
            except Exception as e:
                logger.error(f"Error calculating planet {name}: {e}")
                return jsonify({"error": f"Error calculating planet {name}: {e}"}), 500

        # ASCとMCを計算
        try:
            # swe.houses は (ハウスカスプの配列, ASCとMCの配列) のタプルを返す
            # ASCとMCの配列は ascmc[0]がASC, ascmc[1]がMC
            houses, ascmc = swe.houses(jd, lat, lon)
            result["ASC"] = round(ascmc[0], 2)
            result["MC"] = round(ascmc[1], 2)
        except Exception as e:
            logger.error(f"Error calculating houses/ascmc: {e}")
            return jsonify({"error": f"Error calculating houses/ascmc: {e}"}), 500

        # 成功レスポンス
        return jsonify(result), 200
    except Exception as e:
        # 予期せぬエラーの捕捉
        logger.exception("An unexpected error occurred during astro calculation.")
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500