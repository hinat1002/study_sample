from flask import Flask, render_template, request, redirect
import pandas as pd
import datetime
from zoneinfo import ZoneInfo


def get_data():
  data = pd.read_csv('data.csv', header=0, dtype=str)
  return data


# 状態(勉強中かどうか)の取得
def get_state():
  data = get_data()
  state = int(data.iloc[0, 7])
  if state == 1:
    msg = "(勉強中)"
  elif state == 0:
    msg = "(休憩中)"
  else:
    msg = "(エラー)"
  return msg


def get_index():
  data = get_data()
  index = int(data.iloc[0, 8])
  return index


def get_date_index():
  data = get_data()
  date_index = int(data.iloc[0, 9])
  return date_index


def get_dt():
  dt_now = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
  date = dt_now.strftime('%m/%d')
  time = dt_now.strftime('%H:%M')
  HM = time.split(":")
  H = int(HM[0])
  if H <= 3:
    HM[0] = str(H + 24)
    time = ":".join(HM)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    date = yesterday.strftime('%m/%d')
  return date, time


def get_note():
  data = get_data()
  index = get_index()
  date_index = get_date_index()
  note = data.iloc[index - date_index, 5]
  return note


def save_note(note):
  data = get_data()
  index = get_index()
  date_index = get_date_index()
  data.iloc[index - date_index, 5] = note
  data.to_csv('data.csv', index=False)


app = Flask('app')


@app.route('/')
def index():
  state = get_state()
  return render_template('index.html', state=state)


@app.route('/work_start')
def work_start():
  state = get_state()
  return render_template('work_start.html', state=state)


@app.route('/work_end')
def work_end():
  state = get_state()
  return render_template('work_end.html', state=state)


@app.route('/top')
def top():
  state = get_state()
  return render_template('index.html', state=state)


@app.route('/work_start_now')
def work_start_now():
  state = get_state()
  if state == "(勉強中)":
    return render_template('work_start_false.html', state=state)
  elif state == "(休憩中)":
    data = get_data()
    index = get_index()
    date, time = get_dt()
    data.iloc[index, 0] = date
    data.iloc[index, 1] = time
    if index != 0:
      y_date = data.iloc[index - 1, 0]
      if date != y_date:
        data.iloc[0, 9] = "0"

    data.iloc[0, 7] = "1"
    data.to_csv('data.csv', index=False)
    state = get_state()
    return render_template('work_start_true.html', state=state)
  else:
    return render_template('ELLOR.html', state=state)


@app.route('/work_end_now')
def work_end_now():
  state = get_state()
  if state == "(休憩中)":
    return render_template('work_start_false.html', state=state)
  elif state == "(勉強中)":
    data = get_data()
    index = get_index()
    date_index = get_date_index()
    date, time = get_dt()
    data.iloc[index, 2] = time
    start_time = data.iloc[index, 1]
    HM = time.split(":")
    s_HM = start_time.split(":")
    H = int(HM[0])
    M = int(HM[1])
    s_H = int(s_HM[0])
    s_M = int(s_HM[1])
    if M < s_M:
      H -= 1
      M += 60
    t_H = H - s_H
    t_M = M - s_M
    time_time = str(t_H) + ":" + str(t_M)
    data.iloc[index, 3] = time_time
    if date_index == 0:
      sum_time = time_time
      data.iloc[index, 4] = sum_time
      sum_H = t_H
      sum_M = t_M
    else:
      before_sum_time = data.iloc[index - 1, 4]
      before_sum_HM = before_sum_time.split(":")
      before_sum_H = int(before_sum_HM[0])
      before_sum_M = int(before_sum_HM[1])
      sum_H = before_sum_H + t_H
      sum_M = before_sum_M + t_M
      if sum_M >= 60:
        sum_H += 1
        sum_M -= 60
      sum_time = str(sum_H) + ":" + str(sum_M)
      data.iloc[index, 4] = sum_time

    data.iloc[0, 9] = str(date_index + 1)
    data.iloc[0, 8] = str(index + 1)
    data.iloc[0, 7] = "0"
    data.to_csv('data.csv', index=False)
    state = get_state()
    if sum_M < 10:
      sum_time = str(sum_H) + ":0" + str(sum_M)
    return render_template('work_end_true.html',
                           state=state,
                           sum_time=sum_time)
  else:
    return render_template('ELLOR.html', state=state)


@app.route('/note')
def note():
  state = get_state()
  note = get_note()
  return render_template('note.html', state=state, note=note)


@app.route('/note_write')
def note_write():
  state = get_state()
  note = request.args.get("note")
  save_note(note)
  return render_template('note_true.html', state=state, note=note)


@app.route('/break_time')
def break_time():
  state = get_state()
  return render_template('none.html', state=state)


@app.route('/view')
def view():
  state = get_state()
  return render_template('none.html', state=state)


app.run(host='0.0.0.0')
