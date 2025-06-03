from flask import Flask, request, jsonify
from datetime import datetime
import swisseph as swe

app = Flask(__name__)
swe.set_ephe_path('/usr/share/ephe')

@app.route('/astro', methods=['POST'])
def astro():
    data = request.get_json()
    try:
        birth_dt = datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M')
        lon = float(data['longitude'])
        lat = float(data['latitude'])

        jd = swe.julday(birth_dt.year, birth_dt.month, birth_dt.day,
                        birth_dt.hour + birth_dt.minute / 60.0)

        result = {}

        for i, name in zip(range(10), ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
                                       'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']):
            planet = swe.calc_ut(jd, i)[0]
            result[name] = round(planet, 2)

        houses, ascmc = swe.houses(jd, lat, lon)
        result["ASC"] = round(ascmc[0], 2)
        result["MC"] = round(ascmc[1], 2)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)