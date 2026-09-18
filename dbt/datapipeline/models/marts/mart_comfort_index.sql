WITH BASE AS (
	SELECT
		AQ.CITY,
		AQ.EXTRACTED_AT,
		AQ.FORECAST_DAY,
		AVG_DAILY_TEMPERATURE,
		AVG_DAILY_DUST_VALUE,
		AVG_DAILY_OZONE,
		AVG_DAILY_UV_INDEX
	FROM {{ref('mart_daily_air_quality')}} AQ
	JOIN {{ref('mart_daily_weather')}} USING (CITY, EXTRACTED_AT, FORECAST_DAY)
),

SCORES AS (
	SELECT
		*,
		-- Temperatura: pico em 23°C, cai 100/15 pontos por grau de distância
		GREATEST(0, LEAST(100, 100 - ABS(AVG_DAILY_TEMPERATURE - 23) * (100.0/15))) AS SCORE_TEMP,

		-- UV: 0-2 ótimo, 11+ péssimo (escala inversa e não-linear)
		GREATEST(0, LEAST(100, 100 - (AVG_DAILY_UV_INDEX * 9))) AS SCORE_UV,

		-- Ozônio: 0-100 µg/m³ = bom (score alto), acima disso cai
		GREATEST(0, LEAST(100, 100 - GREATEST(AVG_DAILY_OZONE - 60, 0) * 1.0)) AS SCORE_OZONE,

		-- Dust: quanto menor, melhor; acima de 50 µg/m³ já é ruim
		GREATEST(0, LEAST(100, 100 - AVG_DAILY_DUST_VALUE * 2)) AS SCORE_DUST
	FROM BASE
),

COMFORT_INDEX AS (
	SELECT
		CITY,
		EXTRACTED_AT,
		FORECAST_DAY,
		ROUND((
			SCORE_TEMP  * 0.40 +
			SCORE_UV    * 0.20 +
			SCORE_OZONE * 0.20 +
			SCORE_DUST  * 0.20
		)::NUMERIC, 1) AS COMFORT_INDEX
	FROM SCORES
)

SELECT
	CITY,
	EXTRACTED_AT,
	FORECAST_DAY,
	COMFORT_INDEX,
	CASE
		WHEN COMFORT_INDEX >= 75 THEN 'Comfortable'
		WHEN COMFORT_INDEX >= 50 THEN 'Moderate'
		ELSE 'Uncomfortable'
	END AS CLASS
FROM COMFORT_INDEX