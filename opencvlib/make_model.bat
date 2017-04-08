@echo off
REM sqlacodegen --outfile digikam_models.py --noindexes --nojoined --noviews --noinflect --tables Tags sqlite:///C:/Users/graham~1/OneDrive/Documents/PHD/images/digikam4.db
echo Creating model in %cd%\model_sqlacodegen.py
C:\Python352\Scripts\sqlacodegen --outfile ./model_sqlacodegen.py sqlite:///C:/Users/graham~1/OneDrive/Documents/PHD/images/digikam4.db
pause