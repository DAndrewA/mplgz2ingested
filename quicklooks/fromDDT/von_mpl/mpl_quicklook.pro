; $Id: mpl_quicklook.pro,v 1.4 2015/03/24 13:00:03 dturner Exp $
;
; This script creates a quicklook image for the MPL data from Greenland
;

pro mpl_quicklook, date, $
	do_backsub=do_backsub, do_rangesq=do_rangesq, do_overlap=do_overlap, $
	dosaveimage=dosaveimage, dostop=dostop

if(n_elements(dosaveimage) eq 0) then dosaveimage = 1

mnth = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
dloadct,42

if(date lt 0) then filename = "smtmplpol*cdf" $
else filename = string(format='(A,I0,A)',"smtmplpol*",date(0),"*cdf")

files = findfile(filename, count=count)
for ii=0,count-1 do begin
  fid = ncdf_open(files(ii))
  ncdf_varget,fid,'base_time',bt
  ncdf_varget,fid,'time_offset',to
  ncdf_varget,fid,'energy',emonx
  ncdf_varget,fid,'mn_background_1',bck1x
  ncdf_varget,fid,'mn_background_2',bck2x
  ncdf_varget,fid,'backscatter_1',sig1x
  ncdf_varget,fid,'backscatter_2',sig2x
  ncdf_varget,fid,'height',htx
  ncdf_varget,fid,'temp_detector',tempdx
  ncdf_varget,fid,'temp_telescope',temptx
  ncdf_varget,fid,'temp_laser',templx
  ncdf_close,fid

  if(ii eq 0) then begin
    secs = bt+to
    ht   = htx
    emon = emonx
    bck1 = bck1x
    bck2 = bck2x
    sig1 = transpose(sig1x)
    sig2 = transpose(sig2x)
    tempd = tempdx
    tempt = temptx
    templ = templx
  endif else begin
    if(n_elements(htx) ne n_elements(ht)) then continue
    secs = [secs,bt+to]
    emon = [emon,emonx]
    bck1 = [bck1,bck1x]
    bck2 = [bck2,bck2x]
    sig1 = [sig1,transpose(sig1x)]
    sig2 = [sig2,transpose(sig2x)]
    tempd = [tempd,tempdx]
    tempt = [tempt,temptx]
    templ = [templ,templx]
  endelse
endfor
  sig1 = transpose(sig1)
  sig2 = transpose(sig2)
  systime2ymdhms,secs,yy,mm,dd,hh,nn,ss,hour=hour
  ptitle = string(format='(A,I0,1x,A,1x,I0,A)','ICECAPS MPL Data for ', $
  		dd(0),mnth(mm(0)-1),yy(0),' : ')
  outfile = string(format='(A,I0,I2.2,I2.2,A,3(I2.2),A)','smtmpl_quicklook.', $
  		yy(0),mm(0),dd(0),'.',hh(0),nn(0),ss(0),'.png')

	; This overlap correction was a simple estimation using real background
	; subtracted, range corrected data and assuming a linear trend from 
	; 2.4 km to the surface using data at 1800 on 31 Jan 2011 at Summit
  ocorr = [0.00530759, 0.0583835, 0.110524, 0.174668, 0.246036, 0.333440, 0.421466, $
		0.510560, 0.599191, 0.676644, 0.744512, 0.808004, 0.848976, $
		0.890453, 0.959738, 0.975302, 1.0, 1.0]
  oht = [0.0149896, 0.164886, 0.314782, 0.464678, 0.614575, 0.764471, 0.914367, $
		1.06426, 1.21416, 1.36406, 1.51395, 1.66385, 1.81374, 1.96364, $
		2.11354, 2.26343, 2.5, 20]
  olap = interpol(ocorr, oht, ht)

	; Do the background subtraction and range normalization, if indicated
	; Note that range normalization automatically implies background subtraction
  if(keyword_set(do_rangesq)) then begin
    for i=0,n_elements(hour)-1 do begin
      sig1(*,i) = (sig1(*,i) - bck1(i)) * ht * ht
      sig2(*,i) = (sig2(*,i) - bck2(i)) * ht * ht
      if(keyword_set(do_overlap)) then begin
        sig1(*,i) = sig1(*,i) / olap
        sig2(*,i) = sig2(*,i) / olap
      endif
    endfor
  endif else if(keyword_set(do_backsub)) then begin
    for i=0,n_elements(hour)-1 do begin
      sig1(*,i) = (sig1(*,i) - bck1(i))
      sig2(*,i) = (sig2(*,i) - bck2(i))
    endfor
  endif

  		; Insert any black bars that are needed into the data
  			; Gap at the beginning
  blankprofile = replicate(-999.,n_elements(ht))
  if(min(hour) gt 10/60.) then begin
    hour = [0,min(hour)-0.001,hour]
    emon = [-999,-999,emon]
    bck1 = [-999,-999,bck1]
    bck2 = [-999,-999,bck2]
    tempd = [-999,-999,tempd]
    templ = [-999,-999,templ]
    tempt = [-999,-999,tempt]
    sig1  = transpose([transpose(blankprofile),transpose(blankprofile),transpose(sig1)])
    sig2  = transpose([transpose(blankprofile),transpose(blankprofile),transpose(sig2)])
  endif

  			; Gap at the end
  if(max(hour) lt 24-10/60.) then begin
    hour = [hour,max(hour)+0.001,23.9999]
    emon = [emon,-999,-999]
    bck1 = [bck1,-999,-999]
    bck2 = [bck2,-999,-999]
    tempd = [tempd,-999,-999]
    templ = [templ,-999,-999]
    tempt = [tempt,-999,-999]
    sig1  = transpose([transpose(sig1),transpose(blankprofile),transpose(blankprofile)])
    sig2  = transpose([transpose(sig2),transpose(blankprofile),transpose(blankprofile)])
  endif

			; Gaps in the middle will be blotted out down below...
;  n = n_elements(hour)-1
;  del = hour(1:n)-hour(0:n-1)
;  foo = where(del gt 10/60., nfoo)
;  for j=0,nfoo do begin
;    a = 0		; I need to implement this sometime...
;  endfor

  if(!d.name eq 'X') then window,!d.window+1,xs=640,ys=950 $
  else if(!d.name eq 'Z') then begin
    device,set_resolution=[640,950],set_character_size=[6,9],set_colors=256l
    erase
  endif

  xtit = string(format='(I2.2)',[0,3,6,9,12,15,18,21,24])
  xr   = [min(float(xtit)),max(float(xtit))]
  xm   = 6
  ytit = string(format='(I0)',[0,2,4,6,8])
  yr   = [min(float(ytit)),max(float(ytit))]
  ym   = 10
  if(keyword_set(do_rangesq)) then ztit = string(format='(I0)',[0,4]) $
  else ztit = string(format='(I0)',[0,8])
  zr   = [min(float(ztit)),max(float(ztit))]
  zm   = 10
  !p.multi=[0,0,4]
  pchars = 2.1
  qchars = 1.2
  dcontour,sig1,hour,ht,$
  	'Hour [UTC]', xtit, xr, xm, 'Altitude [km AGL]', ytit, yr, ym, $
	'Signal', ztit, zr(0), zr(1), zm, /no_colorbar, $
	[0,0.75,1,1], [0,0.75,1,1], pchars, ptitle + ' Signal_1'

        ; Black out the temporal gaps in the data
  n = n_elements(secs)
  deltat = secs(1:n-1) - secs(0:n-2)
  tres = median(deltat)   
  foo = where(deltat gt 3*tres+1, nfoo)
  for j=0,nfoo-1 do begin
    if(!x.crange(0) le hour(foo(j)) and hour(foo(j)) lt !x.crange(1)) then $
      polyfill,[hour(foo(j)),hour(foo(j)),hour(foo(j)+1),hour(foo(j)+1),hour(foo(j))],$
                [!y.crange(1),!y.crange(0),!y.crange,!y.crange(1)],color=0
  endfor        

  dcontour,sig2,hour,ht,$
  	'Hour [UTC]', xtit, xr, xm, 'Altitude [km AGL]', ytit, yr, ym, $
	'Signal', ztit, zr(0), zr(1), zm, /no_colorbar, $
	[0,0.50,1,0.75], [0,0.50,1,0.75], pchars, ptitle + ' Signal_2'

        ; Black out the temporal gaps in the data
  for j=0,nfoo-1 do begin
    if(!x.crange(0) le hour(foo(j)) and hour(foo(j)) lt !x.crange(1)) then $
      polyfill,[hour(foo(j)),hour(foo(j)),hour(foo(j)+1),hour(foo(j)+1),hour(foo(j))],$
                [!y.crange(1),!y.crange(0),!y.crange,!y.crange(1)],color=0
  endfor        

  !p.region=[0,0.25,1,0.50]
  tmp = [tempd,templ,tempt]
  bar = where(tmp gt -100,nbar)
  if(nbar gt 0) then tmp = tmp(bar)
  plot,hour,tempd,chars=pchars,yr=[min(tmp),max(tmp)], $
  	xr=xr, /xst, xticks=n_elements(xtit)-1, xtickn=xtit, xminor=xm, $
	xtit='Hour [UTC]', $
	ytit='Temperature [C]', xticklen=-0.02, yticklen=-0.01
  oplot,hour,templ,color=210
  oplot,hour,tempt,color=60
  xyouts,0.53,0.49,/nor,chars=qchars,align=0.5,'Detector Temp'
  xyouts,0.23,0.49,/nor,chars=qchars,align=0.5,'Laser Temp', color=210
  xyouts,0.83,0.49,/nor,chars=qchars,align=0.5,'Telescope Temp', color=60

        ; Black out the temporal gaps in the data
  for j=0,nfoo-1 do begin
    if(!x.crange(0) le hour(foo(j)) and hour(foo(j)) lt !x.crange(1)) then $
      polyfill,[hour(foo(j)),hour(foo(j)),hour(foo(j)+1),hour(foo(j)+1),hour(foo(j))],$
                [0.99*!y.crange(1),!y.crange(0),!y.crange,0.99*!y.crange(1)],color=255
  endfor        

  !p.region=[0,0.00,1,0.25]
  plot,hour,emon,chars=pchars, $
	title='Laser Output Energy', $
  	xr=xr, /xst, xticks=n_elements(xtit)-1, xtickn=xtit, xminor=xm, $
	xtit='Hour [UTC]', min_val=-10, $
	ytit='Laser Energy [micro Joules]', xticklen=-0.02, yticklen=-0.01

        ; Black out the temporal gaps in the data
  for j=0,nfoo-1 do begin
    if(!x.crange(0) le hour(foo(j)) and hour(foo(j)) lt !x.crange(1)) then $
      polyfill,[hour(foo(j)),hour(foo(j)),hour(foo(j)+1),hour(foo(j)+1),hour(foo(j))],$
                [0.99*!y.crange(1),!y.crange(0),!y.crange,0.99*!y.crange(1)],color=255
  endfor        
  !p.multi=0
  !p.region=0

  if(dosaveimage eq 1) then saveimage,/cube,outfile

  if(keyword_set(dostop)) then stop,'Stopped inside routine'
end
