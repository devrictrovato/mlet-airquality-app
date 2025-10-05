WITH base_data AS (
  SELECT
    *,
    CASE
      WHEN aqi = 'N/A' THEN
        CASE WHEN rand(42) <= 0.75 THEN 'Unhealthy' ELSE 'Unhealthy for Sensitive Groups' END
      WHEN aqi = 'no data' THEN
        CASE WHEN rand(42) <= 0.5 THEN 'Very Unhealthy' ELSE 'Hazardous' END
      ELSE aqi
    END AS aqi_cleaned
  FROM raw_data
),

data_cleaned AS (
  SELECT
    date,
    station,
    country,
    state,
    city,
    aqi_cleaned AS aqi,
    CASE WHEN pm25 < 0 THEN NULL ELSE pm25 END AS pm25,
    CASE WHEN pm10 < 0 THEN NULL ELSE pm10 END AS pm10,
    CASE WHEN no2 < 0 THEN NULL ELSE no2 END AS no2,
    CASE WHEN so2 < 0 THEN NULL ELSE so2 END AS so2,
    CASE WHEN co < 0 THEN NULL ELSE co END AS co,
    CASE WHEN temperature < 0 THEN NULL ELSE temperature END AS temperature,
    CASE WHEN pressure < 0 THEN NULL ELSE pressure END AS pressure,
    CASE WHEN humidity < 0 THEN NULL ELSE humidity END AS humidity,
    CASE WHEN wind < 0 THEN NULL ELSE wind END AS wind
  FROM base_data
),

max_state AS (
  SELECT
    state AS state_max,
    MAX(pm25) AS pm25_max,
    MAX(pm10) AS pm10_max,
    MAX(no2) AS no2_max,
    MAX(so2) AS so2_max,
    MAX(co) AS co_max,
    MAX(temperature) AS temperature_max,
    MAX(pressure) AS pressure_max,
    MAX(humidity) AS humidity_max,
    MAX(wind) AS wind_max
  FROM data_cleaned
  WHERE aqi IN ('Hazardous', 'Very Unhealthy')
  GROUP BY state
),

mean_country AS (
  SELECT
    country AS country_mean,
    AVG(pm25) AS pm25_mean_country,
    AVG(pm10) AS pm10_mean_country,
    AVG(no2) AS no2_mean_country,
    AVG(so2) AS so2_mean_country,
    AVG(co) AS co_mean_country,
    AVG(temperature) AS temperature_mean_country,
    AVG(pressure) AS pressure_mean_country,
    AVG(humidity) AS humidity_mean_country,
    AVG(wind) AS wind_mean_country
  FROM data_cleaned
  WHERE aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy')
  GROUP BY country
),

mode_city AS (
  SELECT DISTINCT city,
    FIRST_VALUE(pm25) OVER (PARTITION BY city ORDER BY COUNT(*) OVER (PARTITION BY city, pm25) DESC) AS pm25_mode_city,
    FIRST_VALUE(pm10) OVER (PARTITION BY city ORDER BY COUNT(*) OVER (PARTITION BY city, pm10) DESC) AS pm10_mode_city,
    FIRST_VALUE(no2)  OVER (PARTITION BY city ORDER BY COUNT(*) OVER (PARTITION BY city, no2) DESC) AS no2_mode_city,
    FIRST_VALUE(so2)  OVER (PARTITION BY city ORDER BY COUNT(*) OVER (PARTITION BY city, so2) DESC) AS so2_mode_city,
    FIRST_VALUE(co)   OVER (PARTITION BY city ORDER BY COUNT(*) OVER (PARTITION BY city, co) DESC) AS co_mode_city,
    FIRST_VALUE(temperature) OVER (PARTITION BY city ORDER BY COUNT(*) OVER (PARTITION BY city, temperature) DESC) AS temperature_mode_city,
    FIRST_VALUE(pressure) OVER (PARTITION BY city ORDER BY COUNT(*) OVER (PARTITION BY city, pressure) DESC) AS pressure_mode_city,
    FIRST_VALUE(humidity) OVER (PARTITION BY city ORDER BY COUNT(*) OVER (PARTITION BY city, humidity) DESC) AS humidity_mode_city,
    FIRST_VALUE(wind) OVER (PARTITION BY city ORDER BY COUNT(*) OVER (PARTITION BY city, wind) DESC) AS wind_mode_city
  FROM data_cleaned
  WHERE aqi = 'Good'
),

mean_station AS (
  SELECT
    station AS station_mean,
    AVG(pm25) AS pm25_mean_station,
    AVG(pm10) AS pm10_mean_station,
    AVG(no2) AS no2_mean_station,
    AVG(so2) AS so2_mean_station,
    AVG(co) AS co_mean_station,
    AVG(temperature) AS temperature_mean_station,
    AVG(pressure) AS pressure_mean_station,
    AVG(humidity) AS humidity_mean_station,
    AVG(wind) AS wind_mean_station
  FROM data_cleaned
  GROUP BY station
),

joined AS (
  SELECT
    d.date            AS date,
    d.station         AS station,
    d.country         AS country,
    d.state           AS state,
    d.city            AS city,
    d.aqi             AS aqi,
    d.pm25            AS pm25,
    d.pm10            AS pm10,
    d.no2             AS no2,
    d.so2             AS so2,
    d.co              AS co,
    d.temperature     AS temperature,
    d.pressure        AS pressure,
    d.humidity        AS humidity,
    d.wind            AS wind,
    
    ms.pm25_max,
    ms.pm10_max,
    ms.no2_max,
    ms.so2_max,
    ms.co_max,
    ms.temperature_max,
    ms.pressure_max,
    ms.humidity_max,
    ms.wind_max,
    
    mc.pm25_mean_country,
    mc.pm10_mean_country,
    mc.no2_mean_country,
    mc.so2_mean_country,
    mc.co_mean_country,
    mc.temperature_mean_country,
    mc.pressure_mean_country,
    mc.humidity_mean_country,
    mc.wind_mean_country,
    
    mo.pm25_mode_city,
    mo.pm10_mode_city,
    mo.no2_mode_city,
    mo.so2_mode_city,
    mo.co_mode_city,
    mo.temperature_mode_city,
    mo.pressure_mode_city,
    mo.humidity_mode_city,
    mo.wind_mode_city,
    
    mst.pm25_mean_station,
    mst.pm10_mean_station,
    mst.no2_mean_station,
    mst.so2_mean_station,
    mst.co_mean_station,
    mst.temperature_mean_station,
    mst.pressure_mean_station,
    mst.humidity_mean_station,
    mst.wind_mean_station

  FROM data_cleaned d
  LEFT JOIN max_state ms     ON d.state = ms.state_max
  LEFT JOIN mean_country mc  ON d.country = mc.country_mean
  LEFT JOIN mode_city mo     ON d.city = mo.city
  LEFT JOIN mean_station mst ON d.station = mst.station_mean
)

SELECT
  j.date,
  j.station,
  j.country,
  j.state,
  j.city,
  j.aqi,

  COALESCE(j.pm25,
    CASE 
      WHEN j.aqi IN ('Hazardous', 'Very Unhealthy') THEN j.pm25_max
      WHEN j.aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy') THEN j.pm25_mean_country
      WHEN j.aqi = 'Good' THEN j.pm25_mode_city
      ELSE j.pm25_mean_station
    END,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.pm25) OVER (PARTITION BY j.aqi)
  ) AS pm25,

  COALESCE(j.pm10,
    CASE 
      WHEN j.aqi IN ('Hazardous', 'Very Unhealthy') THEN j.pm10_max
      WHEN j.aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy') THEN j.pm10_mean_country
      WHEN j.aqi = 'Good' THEN j.pm10_mode_city
      ELSE j.pm10_mean_station
    END,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.pm10) OVER (PARTITION BY j.aqi)
  ) AS pm10,

  COALESCE(j.no2,
    CASE 
      WHEN j.aqi IN ('Hazardous', 'Very Unhealthy') THEN j.no2_max
      WHEN j.aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy') THEN j.no2_mean_country
      WHEN j.aqi = 'Good' THEN j.no2_mode_city
      ELSE j.no2_mean_station
    END,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.no2) OVER (PARTITION BY j.aqi)
  ) AS no2,

  COALESCE(j.so2,
    CASE 
      WHEN j.aqi IN ('Hazardous', 'Very Unhealthy') THEN j.so2_max
      WHEN j.aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy') THEN j.so2_mean_country
      WHEN j.aqi = 'Good' THEN j.so2_mode_city
      ELSE j.so2_mean_station
    END,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.so2) OVER (PARTITION BY j.aqi)
  ) AS so2,

  COALESCE(j.co,
    CASE 
      WHEN j.aqi IN ('Hazardous', 'Very Unhealthy') THEN j.co_max
      WHEN j.aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy') THEN j.co_mean_country
      WHEN j.aqi = 'Good' THEN j.co_mode_city
      ELSE j.co_mean_station
    END,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.co) OVER (PARTITION BY j.aqi)
  ) AS co,

  COALESCE(j.temperature,
    CASE 
      WHEN j.aqi IN ('Hazardous', 'Very Unhealthy') THEN j.temperature_max
      WHEN j.aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy') THEN j.temperature_mean_country
      WHEN j.aqi = 'Good' THEN j.temperature_mode_city
      ELSE j.temperature_mean_station
    END,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.temperature) OVER (PARTITION BY j.aqi)
  ) AS temperature,

  COALESCE(j.pressure,
    CASE 
      WHEN j.aqi IN ('Hazardous', 'Very Unhealthy') THEN j.pressure_max
      WHEN j.aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy') THEN j.pressure_mean_country
      WHEN j.aqi = 'Good' THEN j.pressure_mode_city
      ELSE j.pressure_mean_station
    END,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.pressure) OVER (PARTITION BY j.aqi)
  ) AS pressure,

  COALESCE(j.humidity,
    CASE 
      WHEN j.aqi IN ('Hazardous', 'Very Unhealthy') THEN j.humidity_max
      WHEN j.aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy') THEN j.humidity_mean_country
      WHEN j.aqi = 'Good' THEN j.humidity_mode_city
      ELSE j.humidity_mean_station
    END,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.humidity) OVER (PARTITION BY j.aqi)
  ) AS humidity,

  COALESCE(j.wind,
    CASE 
      WHEN j.aqi IN ('Hazardous', 'Very Unhealthy') THEN j.wind_max
      WHEN j.aqi IN ('Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy') THEN j.wind_mean_country
      WHEN j.aqi = 'Good' THEN j.wind_mode_city
      ELSE j.wind_mean_station
    END,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.wind) OVER (PARTITION BY j.aqi)
  ) AS wind

FROM joined j