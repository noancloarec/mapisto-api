update states SET validity_start=validity_start + INTERVAL '43min' where extract(hour from validity_start)=23 and extract(minutes from validity_start)=17;
update state_names SET validity_start=validity_start + INTERVAL '43min' where extract(hour from validity_start)=23 and extract(minutes from validity_start)=17;
update states SET validity_end=validity_end + INTERVAL '43min' where extract(hour from validity_end)=23 and extract(minutes from validity_end)=17;
update state_names SET validity_end=validity_end + INTERVAL '43min' where extract(hour from validity_end)=23 and extract(minutes from validity_end)=17;
update territories SET validity_start=validity_start + INTERVAL '43min' where extract(hour from validity_start)=23 and extract(minutes from validity_start)=17;
update territories SET validity_end=validity_end + INTERVAL '43min' where extract(hour from validity_end)=23 and extract(minutes from validity_end)=17;

update states SET validity_start=validity_start + INTERVAL '49min' + INTERVAL '56sec' where extract(hour from validity_start)=23 and extract(minutes from validity_start)=10 and extract(seconds from validity_start)=04;
update state_names SET validity_start=validity_start + INTERVAL '49min' + INTERVAL '56sec' where extract(hour from validity_start)=23 and extract(minutes from validity_start)=10 and extract(seconds from validity_start)=04;
update states SET validity_end=validity_end + INTERVAL '49min' + INTERVAL '56sec' where extract(hour from validity_end)=23 and extract(minutes from validity_end)=10 and extract(seconds from validity_end)=04;
update state_names SET validity_end=validity_end + INTERVAL '49min' + INTERVAL '56sec' where extract(hour from validity_end)=23 and extract(minutes from validity_end)=10 and extract(seconds from validity_end)=04;
update territories SET validity_start=validity_start + INTERVAL '49min' + INTERVAL '56sec' where extract(hour from validity_start)=23 and extract(minutes from validity_start)=10 and extract(seconds from validity_start)=04;
update territories SET validity_end=validity_end + INTERVAL '49min' + INTERVAL '56sec' where extract(hour from validity_end)=23 and extract(minutes from validity_end)=10 and extract(seconds from validity_end)=04;


update states SET validity_start=validity_start - INTERVAL '7hours' - INTERVAL '19min' - INTERVAL '56sec' where extract(hour from validity_start)=7 and extract(minutes from validity_start)=19 and extract(seconds from validity_start)=56;
update state_names SET validity_start=validity_start - INTERVAL '7hours' - INTERVAL '19min' - INTERVAL '56sec' where extract(hour from validity_start)=7 and extract(minutes from validity_start)=19 and extract(seconds from validity_start)=56;
update states SET validity_end=validity_end - INTERVAL '7hours' - INTERVAL '19min' - INTERVAL '56sec' where extract(hour from validity_end)=7 and extract(minutes from validity_end)=19 and extract(seconds from validity_end)=56;
update state_names SET validity_end=validity_end - INTERVAL '7hours' - INTERVAL '19min' - INTERVAL '56sec' where extract(hour from validity_end)=7 and extract(minutes from validity_end)=19 and extract(seconds from validity_end)=56;
update territories SET validity_start=validity_start - INTERVAL '7hours' - INTERVAL '19min' - INTERVAL '56sec' where extract(hour from validity_start)=7 and extract(minutes from validity_start)=19 and extract(seconds from validity_start)=56;
update territories SET validity_end=validity_end - INTERVAL '7hours' - INTERVAL '19min' - INTERVAL '56sec' where extract(hour from validity_end)=7 and extract(minutes from validity_end)=19 and extract(seconds from validity_end)=56;

update states SET validity_start=validity_start - INTERVAL '11hours' - INTERVAL '49min' - INTERVAL '56sec' where extract(hour from validity_start)=11 and extract(minutes from validity_start)=49 and extract(seconds from validity_start)=56;
update state_names SET validity_start=validity_start - INTERVAL '11hours' - INTERVAL '49min' - INTERVAL '56sec' where extract(hour from validity_start)=11 and extract(minutes from validity_start)=49 and extract(seconds from validity_start)=56;
update states SET validity_end=validity_end - INTERVAL '11hours' - INTERVAL '49min' - INTERVAL '56sec' where extract(hour from validity_end)=11 and extract(minutes from validity_end)=49 and extract(seconds from validity_end)=56;
update state_names SET validity_end=validity_end - INTERVAL '11hours' - INTERVAL '49min' - INTERVAL '56sec' where extract(hour from validity_end)=11 and extract(minutes from validity_end)=49 and extract(seconds from validity_end)=56;
update territories SET validity_start=validity_start - INTERVAL '11hours' - INTERVAL '49min' - INTERVAL '56sec' where extract(hour from validity_start)=11 and extract(minutes from validity_start)=49 and extract(seconds from validity_start)=56;
update territories SET validity_end=validity_end - INTERVAL '11hours' - INTERVAL '49min' - INTERVAL '56sec' where extract(hour from validity_end)=11 and extract(minutes from validity_end)=49 and extract(seconds from validity_end)=56;

update states SET validity_start=validity_start - INTERVAL '2hours' - INTERVAL '44min' - INTERVAL '54sec' where extract(hour from validity_start)=2 and extract(minutes from validity_start)=44 and extract(seconds from validity_start)=54;
update state_names SET validity_start=validity_start - INTERVAL '2hours' - INTERVAL '44min' - INTERVAL '54sec' where extract(hour from validity_start)=2 and extract(minutes from validity_start)=44 and extract(seconds from validity_start)=54;
update states SET validity_end=validity_end - INTERVAL '2hours' - INTERVAL '44min' - INTERVAL '54sec' where extract(hour from validity_end)=2 and extract(minutes from validity_end)=44 and extract(seconds from validity_end)=54;
update state_names SET validity_end=validity_end - INTERVAL '2hours' - INTERVAL '44min' - INTERVAL '54sec' where extract(hour from validity_end)=2 and extract(minutes from validity_end)=44 and extract(seconds from validity_end)=54;
update territories SET validity_start=validity_start - INTERVAL '2hours' - INTERVAL '44min' - INTERVAL '54sec' where extract(hour from validity_start)=2 and extract(minutes from validity_start)=44 and extract(seconds from validity_start)=54;
update territories SET validity_end=validity_end - INTERVAL '2hours' - INTERVAL '44min' - INTERVAL '54sec' where extract(hour from validity_end)=2 and extract(minutes from validity_end)=44 and extract(seconds from validity_end)=54;


update states SET validity_start=validity_start - INTERVAL '12hours' where extract(hour from validity_start)=12 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update state_names SET validity_start=validity_start - INTERVAL '12hours' where extract(hour from validity_start)=12 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update states SET validity_end=validity_end - INTERVAL '12hours' where extract(hour from validity_end)=12 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;
update state_names SET validity_end=validity_end - INTERVAL '12hours' where extract(hour from validity_end)=12 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;
update territories SET validity_start=validity_start - INTERVAL '12hours' where extract(hour from validity_start)=12 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update territories SET validity_end=validity_end - INTERVAL '12hours' where extract(hour from validity_end)=12 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;


update states SET validity_start=validity_start + INTERVAL '21min' + INTERVAL '30sec'  where extract(hour from validity_start)=23 and extract(minutes from validity_start)=38 and extract(seconds from validity_start)=30;
update state_names SET validity_start=validity_start + INTERVAL '21min' + INTERVAL '30sec'  where extract(hour from validity_start)=23 and extract(minutes from validity_start)=38 and extract(seconds from validity_start)=30;
update states SET validity_end=validity_end + INTERVAL '21min' + INTERVAL '30sec'  where extract(hour from validity_end)=23 and extract(minutes from validity_end)=38 and extract(seconds from validity_end)=30;
update state_names SET validity_end=validity_end + INTERVAL '21min' + INTERVAL '30sec'  where extract(hour from validity_end)=23 and extract(minutes from validity_end)=38 and extract(seconds from validity_end)=30;
update territories SET validity_start=validity_start + INTERVAL '21min' + INTERVAL '30sec'  where extract(hour from validity_start)=23 and extract(minutes from validity_start)=38 and extract(seconds from validity_start)=30;
update territories SET validity_end=validity_end + INTERVAL '21min' + INTERVAL '30sec'  where extract(hour from validity_end)=23 and extract(minutes from validity_end)=38 and extract(seconds from validity_end)=30;

update states SET validity_start=validity_start + INTERVAL '1hours' where extract(hour from validity_start)=23 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update state_names SET validity_start=validity_start + INTERVAL '1hours' where extract(hour from validity_start)=23 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update states SET validity_end=validity_end + INTERVAL '1hours' where extract(hour from validity_end)=23 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;
update state_names SET validity_end=validity_end + INTERVAL '1hours' where extract(hour from validity_end)=23 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;
update territories SET validity_start=validity_start + INTERVAL '1hours' where extract(hour from validity_start)=23 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update territories SET validity_end=validity_end + INTERVAL '1hours' where extract(hour from validity_end)=23 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;

update states SET validity_start=validity_start + INTERVAL '2hours' where extract(hour from validity_start)=22 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update state_names SET validity_start=validity_start + INTERVAL '2hours' where extract(hour from validity_start)=22 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update states SET validity_end=validity_end + INTERVAL '2hours' where extract(hour from validity_end)=22 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;
update state_names SET validity_end=validity_end + INTERVAL '2hours' where extract(hour from validity_end)=22 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;
update territories SET validity_start=validity_start + INTERVAL '2hours' where extract(hour from validity_start)=22 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update territories SET validity_end=validity_end + INTERVAL '2hours' where extract(hour from validity_end)=22 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;

update states SET validity_start=validity_start + INTERVAL '6hours' where extract(hour from validity_start)=18 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update state_names SET validity_start=validity_start + INTERVAL '6hours' where extract(hour from validity_start)=18 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update states SET validity_end=validity_end + INTERVAL '6hours' where extract(hour from validity_end)=18 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;
update state_names SET validity_end=validity_end + INTERVAL '6hours' where extract(hour from validity_end)=18 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;
update territories SET validity_start=validity_start + INTERVAL '6hours' where extract(hour from validity_start)=18 and extract(minutes from validity_start)=0 and extract(seconds from validity_start)=0;
update territories SET validity_end=validity_end + INTERVAL '6hours' where extract(hour from validity_end)=18 and extract(minutes from validity_end)=0 and extract(seconds from validity_end)=0;
