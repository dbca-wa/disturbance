select lorg.name,ap.lodgement_number AS app_no,pp.title AS prop_title,
TO_CHAR(ap.issue_date, 'yyyy-mm-dd') AS appissdate,
TO_CHAR(ap.start_date, 'yyyy-mm-dd') AS appstadate,  
ap.status AS appstatus, 
(select string_agg(DISTINCT dp.lodgement_number::text, ',' ORDER BY dp.lodgement_number::text)
 from disturbance_approval ap2
 join disturbance_proposal dp on dp.id = ap2.current_proposal_id
 where ap2.lodgement_number = ap.lodgement_number) AS assocprop,
pp.proposal_type AS proptype, 
concat('/internal/proposal/', pp.id) AS propurl,
pp.activity,pp.shapefile_geom AS geometry from disturbance_proposal pp LEFT JOIN disturbance_approval ap 
ON ap.current_proposal_id = pp.id LEFT JOIN disturbance_organisation org ON org.id = pp.applicant_id 
LEFT JOIN accounts_organisation lorg ON org.organisation_id = lorg.id 
FULL JOIN disturbance_approval app ON ap.lodgement_number = app.lodgement_number 
WHERE pp.processing_status NOT IN ('temp', 'declined', 'discarded') AND pp.shapefile_geom IS NOT NULL;