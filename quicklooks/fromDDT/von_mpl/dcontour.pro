; $Id: dcontour.pro,v 1.3 2007/10/09 17:16:11 dturner Exp $
;+
; Abstract:
;	This routine is a generalization of the routine used to create the time-height
;    contours in the RLPROF routines.  Most of the parameters are entered in below as
;    required arguments.  The p.multi must be defined ahead of time, and the p.region
;    is passed in for both the cross-section and the color bar.  This provides an
;    emmense amount of control, as one cross-section may be put on the plot, or
;    ten.  
; 
; Author:
;	Dave Turner
;		Pacific Northwest National Laboratory
;		University of Wisconsin - Madison
;
; Date:
;	May 2002
;
; Call:		; Note that the arguments are all required...
    pro dcontour, $
    	data, $				; 2-D data
    	time, $				; 1-D data for the x-axis
	height, $			; 1-D data for the y-axis
	time_unit, $			; label for the x-axis
	time_ticks, $			; x-axis labels 
	time_range, $			; x-axis range
	time_minor, $			; number of minor ticks on x-axis
	height_unit, $			; label for y-axis
	height_ticks, $			; y-axis labels
	height_range, $			; y-axis range
	height_minor, $			; number of minor ticks on y-axis
	cbar_unit, $			; label for color bar
	cbar_ticks, $			; color bar labels
	cbar_min, $			; minimum value for color bar (and 2-D data)
	cbar_max, $			; maximum value for color bar (and 2-D data)
	cbar_minor, $			; number of minor color bar ticks
	image_region, $			; plot region for 2-D data
	cbar_region, $			; plot region for color bar
	pchars, $			; character size
	ptitle, $			; title, displayed on top of 2-D image
	no_colorbar=no_colorbar, $		; Set this prevent display of color bar
	hor_colorbar=hor_colorbar, $		; Set this for a horizontal color bar
	yticklen=yticklen, $		; Set this to change the ytick length on plot
	xticklen=xticklen, $		; Set this to change the xtick length on plot
	cyticklen=cyticklen, $		; Set this to change the ytick length on colorbar
	cxticklen=cxticklen		; Set this to change the xtick length on colorbar
;-

  if(n_elements(yticklen) eq 0)  then  yticklen = 0.01
  if(n_elements(xticklen) eq 0)  then  xticklen = 0.02
  if(n_elements(cyticklen) eq 0) then cyticklen = 0.01
  if(n_elements(cxticklen) eq 0) then cxticklen = 0.01

  foo = where(height_range(0) le height and height le height_range(1), nfoo)
  if(nfoo le 3) then begin
    print, 'No data found in the height range'
    xyouts,mean(image_region([0,2])),mean(image_region([1,3])),align=0.5,/normal, $
        'No Data'
    return
  endif
  data1 = data(foo,*)
  height1 = height(foo)

  foo = where(time_range(0) le time and time le time_range(1), nfoo)
  if(nfoo le 3) then begin
    print, 'No data found in the time range'
    xyouts,mean(image_region([0,2])),mean(image_region([1,3])),align=0.5,/normal, $
        'No Data'
    return
  endif
  data1 = data1(*,foo)
  time1 = time(foo)

  data1 = (data1 > cbar_min) < cbar_max
  levels = (data1 - cbar_min) / float(cbar_max - cbar_min) * (!d.table_size-1)

  if(not keyword_set(no_colorbar)) then begin
    !p.region = cbar_region
    a = findgen(256)/255.0 * (!d.table_size - 1)
    b = [transpose(a),transpose(a)]
    if(keyword_set(hor_colorbar)) then begin
      shade_surf, transpose(b), a, [0,1], ax=90, az=0, zcharsize=0.01, zvalue=0, $
        ystyle=1, xstyle=1, zstyle=4, $
        shades=transpose(b), color=0, charsize=pchars, xticklen=-1*cxticklen, $
        xtitle=cbar_unit, xtickname=cbar_ticks, yticklen=cyticklen, $
        xticks=n_elements(cbar_ticks)-1, xchars=0.01, ychars=0.01, yticks=1
      plot, [cbar_min,cbar_max], [-1,1], /noerase, /nodata, $
        ystyle=1, xstyle=1, yr=[0,1], xr=[cbar_min,cbar_max], ycharsize=0.01, $
        xtitle=cbar_unit, xticks=n_elements(cbar_ticks)-1, xtickn=cbar_ticks, $
	yticklen=cyticklen, color=0, charsize=pchars, yticks=1
    endif else begin
      shade_surf, b, [0,1], a, ax=90, az=0, zcharsize=0.01, zvalue=0, $
        xstyle=1, ystyle=1, zstyle=4, $
        shades=b, color=0, charsize=pchars, yticklen=-1*cyticklen, $
        ytitle=cbar_unit, ytickname=cbar_ticks, xticklen=cxticklen, $
        yticks=n_elements(cbar_ticks)-1, ychars=0.01, xchars=0.01, xticks=1
      plot, [-1,1], [cbar_min,cbar_max], /noerase, /nodata, $
        xstyle=1, ystyle=1, xr=[0,1], yr=[cbar_min,cbar_max], xcharsize=0.01, $
        ytitle=cbar_unit, yticks=n_elements(cbar_ticks)-1, ytickn=cbar_ticks, $
	xticklen=cxticklen, color=0, charsize=pchars, xticks=1
    endelse
  endif

  !p.region = image_region
  shade_surf, transpose(data1), time1, height1, ax=90, az=0, zchars=0.01, zvalue=0, $
    color=0, /xst, /yst, yr=height_range, xr=time_range, $
    xticks=n_elements(time_ticks)-1, xtickn=time_ticks, xminor=time_minor, $
    yticks=n_elements(height_ticks)-1, ytickn=height_ticks, yminor=height_minor, $
    xticklen=-1*xticklen, yticklen=-1*yticklen, chars=pchars, shade=transpose(levels)
  plot, time_range, height_range, /xst, /yst, /noerase, /nodata, $
    xticks=n_elements(time_ticks)-1, xtickn=time_ticks, xminor=time_minor, $
    yticks=n_elements(height_ticks)-1, ytickn=height_ticks, yminor=height_minor, $
    xticklen=-1*xticklen, yticklen=-1*yticklen, ytit=height_unit, xtit=time_unit, $
    chars=pchars, color=0, title=ptitle

end

