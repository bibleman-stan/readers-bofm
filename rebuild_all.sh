#!/bin/bash

# This script rebuilds all books using the build_book.py script

for book in *; do
    if [ -d "$book" ]; then
        echo "Building $book..."
        python3 "$book/build_book.py"
    fi
done
