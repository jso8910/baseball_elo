# Baseball Elo

Pretty simple. Works pretty well, not so well to be able to predict matchup wOBA (an attempt is in `apply_elo.py` but there's a lot of error, for example, it gives peak Barry Bonds an ~.390 wOBA against the average pitcher... which is unlikely to be true to say the least). Seems to sometimes have hitters fall down in their rating too much (Bonds fell from 1310 at his peak to 1080 by the end of his career despite still being a great hitter, if a little bit worse than his peak).

Otherwise, I like it. It comes up with rankings that make sense. It was a fun practice.

I think the main thing I should optimize is this: how I derive the Elo weights from the wOBA weights. At the moment it's a little pseudoscientific. I just add 0.5 to everything before adding 0.2 to normal outs and 0.3 to strikeouts and then make an IBB = UBB/3. Should there be more of a bonus for strikeouts? Should I stick with normal wOBA weights, just adding a bit? That would lead to a better wOBA predictiveness, but it wouldn't be entirely effective because it messes up the ratios between the different ratings... but "out" can't be 0 since that would mean a pitcher can never accumulate points. Maybe I should even abandon the wOBA connection and just come up with arbitrary numbers in order to be more of a "this outcome is more impressive for the hitter/pitcher" metric than a "this outcome is more valuable... but also strikeouts are more impressive so I'll give them a value boost". So I'm not sure, but there has to be some solution.

How to use (the virtualenv steps are optional):

```sh
$ python3 -m venv venv
$ . venv/bin/activate
## End of optional steps
$ pip3 install -r requirements.txt
$ python3 download.py
$ ./retrosheet_to_csv.sh
$ python3 calc_averages.py
$ python3 calc_woba_weights.py
$ python3 calc_elo_weights.py
$ python3 evaluate_elo.py
```
