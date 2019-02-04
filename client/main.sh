export PATH=$PATH:~/.local/bin
ps aux |grep python |grep -v 'SimpleHTTPServer' |awk '{print $2}' |xargs kill
python3 main.py
