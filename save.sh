BUILD_DIR="out"
CV_FILENAME="Paolo Lammens - CV"
RESUME_FILENAME="Paolo Lammens - Resume"

BRANCH=$(git branch --show-current)
SAVE_DIR="${BUILD_DIR}/${BRANCH}"
CV_OUT_PATH=${SAVE_DIR}/${CV_FILENAME}.pdf
RESUME_OUT_PATH=${SAVE_DIR}/${RESUME_FILENAME}.pdf

mkdir -p "${SAVE_DIR}"
echo "Saving CV to \"$CV_OUT_PATH\""
cp $BUILD_DIR/cv.pdf "$CV_OUT_PATH"
echo "Saving resume to \"$RESUME_OUT_PATH\""
cp $BUILD_DIR/resume.pdf "$RESUME_OUT_PATH"
