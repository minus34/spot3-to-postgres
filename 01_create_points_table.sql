
DROP TABLE IF EXISTS public.spot3_points CASCADE;
CREATE TABLE public.spot3_points
(
    id                  bigint,
    messenger_id        text,
    messenger_name      text,
    unix_time           bigint,
    message_type        text,
    latitude            numeric(7, 5),
    longitude           numeric(8, 5),
    model_id            text,
    show_custom_message text,
    time_utc            timestamp without time zone,
    battery_state       text,
    hidden              text,
    altitude            smallint,
    geom                geometry(PointM, 4283)
) WITH (OIDS = FALSE) ;
ALTER TABLE public.spot3_points OWNER to postgres;
ALTER TABLE public.spot3_points ADD CONSTRAINT spot3_points_pkey PRIMARY KEY (messenger_id, unix_time);

CREATE INDEX spot3_time_idx ON public.spot3_points USING btree (time_utc);

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
