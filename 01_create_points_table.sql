
DROP TABLE IF EXISTS public.spot3_points CASCADE;
CREATE TABLE public.spot3_points
(
    id            bigint,
    messengerId   text,
    messengerName text,
    unixTime      bigint,
    messageType   text,
    latitude      numeric(7, 5),
    longitude     numeric(8, 5),
    modelId       text,
    showCustomMsg text,
    dateTime      timestamp without time zone,
    batteryState  text,
    hidden        text,
    altitude      smallint,
    geom          geometry(PointM, 4283)
) WITH (OIDS = FALSE) ;
ALTER TABLE public.spot3_points OWNER to postgres;
ALTER TABLE public.spot3_points ADD CONSTRAINT spot3_points_pkey PRIMARY KEY (messengerId, unixTime);

CREATE INDEX spot3_time_idx ON public.spot3_points USING btree (unixTime);

CREATE INDEX spot3_points_geom_idx ON public.spot3_points USING GIST (geom);
ALTER TABLE public.spot3_points CLUSTER ON spot3_points_geom_idx;
