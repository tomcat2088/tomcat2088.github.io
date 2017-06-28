jekyll build --destination ../SquarePants1991.github.io
cd ../SquarePants1991.github.io
git add .
git commit -m "Publish Blog at $(Date)"
git push origin master