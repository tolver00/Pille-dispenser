from flask import Flask, render_template
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import numpy as np

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
	return render_template('gallery.html')


@app.route('/stats.png')
def stats_png():
	x = np.arange(10)
	y = np.arange(10) + np.sin(np.arange(10) / 2.0)
	fig, ax = plt.subplots(figsize=(8, 3))
	ax.plot(x, y, marker='o')
	ax.set_title('Simple example chart')
	ax.set_xlabel('X')
	ax.set_ylabel('Y')
	plt.tight_layout()

	img = io.BytesIO()
	plt.savefig(img, format='png')
	img.seek(0)
	plt.close(fig)
	return app.response_class(img.getvalue(), mimetype='image/png')


if __name__ == '__main__':
	app.run(debug=True)
