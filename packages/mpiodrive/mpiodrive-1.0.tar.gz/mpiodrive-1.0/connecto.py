from flask import redirect, url_for, Flask
from StringIO import StringIO
import os
from smb import smb_structs
from flask import render_template
smb_structs.SUPPORT_SMB2 = False
from smb.SMBConnection import SMBConnection
conn = SMBConnection("p1107955", "17283950", "ceclinux", "ipm.edu.mo", use_ntlm_v2=False)
assert conn.connect("202.175.9.5", 445)
results = conn.listPath('Share', '/ESAP/Hand-Out/')

app = Flask(__name__)


@app.route('/f/<path:filename>')
def show_file(filename):
    temp_fh = StringIO()
    file_attributes, filesize = conn.retrieveFile('Share', '/ESAP/Hand-Out/' + filename, temp_fh)
    localfile = filename.split('/')[-1]
    f = open(os.path.join(os.getcwd() + '/static/', localfile), 'w')
    f.write(temp_fh.getvalue())
    url_for('static', filename=localfile)
    return redirect(url_for('static', filename=localfile), code=301)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def show_dir(path):
    re = conn.listPath('Share',  os.path.join('/ESAP/Hand-Out/', path))
    for i in re:
        i.filename = os.path.join(path, i.filename)
    return render_template('hello.html', files=re)


@app.route('/')
def render(files=None):
    return render_template('hello.html', files=results)

if __name__ == '__main__':
    app.run(debug=True)
