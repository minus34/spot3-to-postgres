
DROP TABLE IF EXISTS public.spot3_points CASCADE;
CREATE TABLE public.spot3_points
(
    id             bigint,
    messengerId    text,
    messengerName  text,
    unixTime       bigint,
    messageType    text,
    latitude       numeric(7, 5),
    longitude      numeric(8, 5),
    modelId        text,
    showCustomMsg  text,
    dateTime       timestamp without time zone,
    batteryState   text,
    hidden         text,
    altitude       smallint,
    messageContent text,
    geom           geometry(PointM, 4283)
) WITH (OIDS = FALSE) ;
ALTER TABLE public.spot3_points OWNER to postgres;
ALTER TABLE public.spot3_points ADD CONSTRAINT spot3_points_pkey PRIMARY KEY (messengerId, unixTime);

CREATE INDEX spot3_time_idx ON public.spot3_points USING btree (unixTime);

CREATE INDEX spot3_points_geom_idx ON public.spot3_points USING GIST (geom);
ALTER TABLE public.spot3_points CLUSTER ON spot3_points_geom_idx;


-- create table of lines with speeds
drop materialized view if exists public.spot3_lines;
create materialized view public.spot3_lines as
    with lines as (
        select messengerid,
               messengername,
               lead(datetime) over (partition by messengerid order by unixtime) as datetime,
               lead(unixtime) over (partition by messengerid order by unixtime) as unixtime,
               lead(unixtime) over (partition by messengerid order by unixtime) - unixtime as time_difference,
               st_distance(geom::geography, lead(geom::geography) over (partition by messengerid order by unixtime)) * 1.3 as distance_m,
               st_makeline(geom, lead(geom) over (partition by messengerid order by unixtime)) as geom
        from public.spot3_points
        where messagetype = 'UNLIMITED-TRACK'
    )
    select row_number() OVER () AS gid,
           messengerid,
           messengername,
           unixtime,
           datetime,
           time_difference,
           distance_m::integer,
           (distance_m / time_difference::float * 3.6)::numeric(4,1) as speed_kmh,
           geom
    from lines;

CREATE INDEX spot3_lines_geom_idx ON public.spot3_lines USING GIST (geom);
ALTER MATERIALIZED VIEW public.spot3_lines CLUSTER ON spot3_lines_geom_idx;
