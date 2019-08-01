
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


-- SAMPLE XML MESSAGE

-- <id>1249024627</id>
-- <messengerId>0-2869374</messengerId>
-- <messengerName>Stephen Lead</messengerName>
-- <unixTime>1564625934</unixTime>
-- <messageType>UNLIMITED-TRACK</messageType>
-- <latitude>-41.66814</latitude>
-- <longitude>145.9467</longitude>
-- <modelId>SPOT3</modelId>
-- <showCustomMsg>Y</showCustomMsg>
-- <dateTime>2019-08-01T02:18:54+0000</dateTime>
-- <batteryState>GOOD</batteryState>
-- <hidden>0</hidden>
-- <altitude>1247</altitude>
