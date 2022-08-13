sudo kill -9 $(ps aux | grep 'demo' | awk '{print $2}') &
