
-- show points with time since last point
select now() - datetime as time_since_record,
       datetime + interval '10 hours' as local_time,
       *
from public.spot3_points
order by unixtime desc;

-- show lines between points
select datetime + interval '10 hours' as local_time,
       *
from public.spot3_lines
order by datetime;

-- daily totals and averages
select date(datetime + interval '10 hours') as day,
       (sum(distance_m)::float / 1000.0)::numeric(4, 1) as distance_km,
       max(datetime) - min(datetime) as duration,
       (sum(distance_m)::float / (max(unixtime) - min(unixtime))::float * 3.6)::numeric(3, 1) as average_speed_inc_breaks
from public.spot3_lines
where geom is not null
group by day
order by day;

-- check-ins
select datetime + interval '10 hours' as local_time,
       *
from public.spot3_points
where messagetype = 'OK'
order by datetime;
