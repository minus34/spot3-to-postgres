



select *
from public.spot3_points
order by unixtime;



delete from public.spot3_points where unixtime <= 1564616366;
