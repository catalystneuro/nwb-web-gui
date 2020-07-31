from flask import jsonify, render_template


def explorer():
    return render_template('explorer/explorer.html')