alter view v_lengths
as
select 
	xsampleid as sampleid
	,xunique_code as unique_code
	,tl_mm
	,lens_subject_distance
	,laser_corr
	,bg_corr
	,fg_corr
	,laser_sans_corr
	,bg_sans_corr
	,fg_sans_corr
 from
(

	(
		select 
			xsampleid
			,xunique_code
			,tl_mm
			,lens_subject_distance
			,[laser lines] as laser_corr
			,[background checker] as bg_corr
			,[foreground checker] as fg_corr
		 from
		(
		select
			sample.sampleid as xsampleid
			,sample.unique_code as xunique_code
			,sample.tl_mm
			,sample.board_board_length_mm + housing_mount.subject_to_lens_conversion_mm as lens_subject_distance
			,sample_length.ref_length_type
			,sample_length.estimate_mm
		from 
			sample_length
			inner join sample on sample_length.sampleid=sample.sampleid
			inner join sample_header on sample.sample_headerid=sample_header.sample_headerid
			inner join housing_mount on housing_mount.housing_mountid = sample.housing_mountid
		where optical_lens_correction=0
		) as source
		PIVOT
		(
		MAX([estimate_mm]) FOR ref_length_type in ([laser lines], [background checker], [foreground checker])
		)
		as pvt
	) as x

	inner join

	(
		select 
			ysampleid
			,[laser lines] as laser_sans_corr
			,[background checker] as bg_sans_corr
			,[foreground checker] as fg_sans_corr
		 from
		(
		select
			sample.sampleid as ysampleid
			,sample.unique_code as yunique_code
			,sample.tl_mm
			,sample.board_board_length_mm + housing_mount.subject_to_lens_conversion_mm as lens_subject_distance
			,sample_length.ref_length_type
			,sample_length.estimate_mm
		from 
			sample_length
			inner join sample on sample_length.sampleid=sample.sampleid
			inner join sample_header on sample.sample_headerid=sample_header.sample_headerid
			inner join housing_mount on housing_mount.housing_mountid = sample.housing_mountid
		where optical_lens_correction=1
		) as source
		PIVOT
		(
		MAX([estimate_mm]) FOR ref_length_type in ([laser lines], [background checker], [foreground checker])
		)
		as pvt
	) as y on x.xsampleid = y.ysampleid

	inner join

		(
		select 
			zsampleid
			,[laser lines] as laser_all_corr
			,[background checker] as bg_all_corr
			,[foreground checker] as fg_all_corr
		 from
		(
		select
			sample.sampleid as zsampleid
			,sample.unique_code as zunique_code
			,sample.tl_mm
			,sample.board_board_length_mm + housing_mount.subject_to_lens_conversion_mm as lens_subject_distance
			,sample_length.ref_length_type
			,sample_length.estimate_mm
		from 
			sample_length
			inner join sample on sample_length.sampleid=sample.sampleid
			inner join sample_header on sample.sample_headerid=sample_header.sample_headerid
			inner join housing_mount on housing_mount.housing_mountid = sample.housing_mountid
		where optical_lens_correction=1 and perspective_correction=1
		) as source
		PIVOT
		(
		MAX([estimate_mm]) FOR ref_length_type in ([laser lines], [background checker], [foreground checker])
		)
		as pvt
	) as z on x.xsampleid = z.zsampleid

)