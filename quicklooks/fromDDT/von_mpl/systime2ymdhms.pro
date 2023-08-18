; $Id: systime2ymdhms.pro,v 1.4 2004/07/28 16:39:17 dturner Exp $
;***********************************************************************************
;+
;Abstract:
; This routine computes converts the seconds since 1-Jan-1970 (systime) into
;    something more readable (YYYY, MM, DD, HH, Min, SS).
;
; Call:
    pro systime2ymdhms, time, yyyy, mm, dd, hh, nn, ss, $
    		dayfraction=dayfraction, hour=hour
;-

  ntime = time + 0.1D                   ; This helps prevent floating point error
  ndays = ntime / (24.0D * 60.0D * 60.0D)
  date_0 = julday(01,01,1970)
  caldat,date_0+long(ndays), mm, dd, yyyy
 
  dayfraction = ndays - long(ndays)
  hh = fix(dayfraction * 24)
  fraction = dayfraction * 24 - hh
  nn = fix(fraction * 60)
  fraction = fraction * 60 - nn
  ss = round(fraction * 60)
 
  hour = hh + nn/60. + ss/3600.

  return
end

