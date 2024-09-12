'''
@web.route('/download/<token>')
async def download(token):
    path = decrypt_path(token)
    return await send_file(path, as_attachment=True)'''