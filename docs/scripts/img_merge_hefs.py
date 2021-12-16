
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
#problem with the hefs files is that they are spread across multiple folders and the folder
#name does not indiate the square. The square is embedded in the 
__doc__ = ('Merge images into pdfs from folders specifically for HEFS. Not for general use.\n'      
           'Uses the config.py instead of cmd line args.'
           )
import shutil
import os.path as _path

from docs.config import ImgMergeHEFSConfig
import funclib.iolib as iolib
import docs.topdf as topdf
import fuckit


def _get_sqid(fname):
    '''parse out square id'''
    _, f, _ = iolib.get_file_parts(fname)
    #int will error if cant be forced - this is basic validation of square id
    return int(f.split('_')[0])


def main():
    all_images = []
    flds = list([_path.normpath(s) for s in ImgMergeHEFSConfig.paths_with_images])

    for x in iolib.file_list_generator1(flds, '*.jpg', recurse=False):
        if 'historic' in iolib.get_file_parts(x)[1].lower():
            all_images.append(x)
#TODO Should make this generic and move it to iolib
    if ImgMergeHEFSConfig.count_only:
        D = {}
        out = []
        for s in all_images:
            d, f, _ = iolib.get_file_parts(s)
            if d in D:
                D[d].append(f)
            else:
                D[d] = [f]
        for k, i in D.items():
            out.append([k, len(i)])
        iolib.writecsv(r'C:\temp\hefs\file_counts.csv', out, inner_as_rows=False, header=['dir','n'])
        print("Exported to C:/temp/hefs/file_counts.csv")
        return

    saveto = _path.normpath(ImgMergeHEFSConfig.output_folder)
    PP = iolib.PrintProgress(len(all_images))
    new_images = []
    #sort files into folders named with the squareid
    print('Sorting images into folder %s' % saveto)
    for f in all_images:
        d, fname, _ = iolib.get_file_parts2(f)

        try:
            sqid = _get_sqid(fname)
        except Exception as e:
            print("Couldn't get square number for file %s. Skipping..." % fname)
            PP.increment()
            continue
   
        copyto = _path.normpath(_path.join(saveto, str(sqid)))
        iolib.create_folder(copyto)
        shutil.copy2(f, copyto)
        new_images.append(_path.normpath(_path.join(copyto, fname)))
        PP.increment()

    #now do the pdf merge
    print('Now creating the pdfs...')
    n = sum(1 for x in iolib.folder_generator(saveto))
    PP.reset(max=n)

    for fld in iolib.folder_generator(saveto):
        pdf_file_name, tmpfld, imgs = topdf.merge_img(fld, save_to_folder=saveto, label_with_file=True, label_with_fld=True, overwrite=True)
        PP.increment()


if __name__ == "__main__":
    main()

