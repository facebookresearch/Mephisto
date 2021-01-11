# Mephisto Review App

A template for an app that can quickly create a review UI for utilization with the ``` mephisto review ``` command

## Usage

1. Create a sample ```data.csv```:

    ```
    This is good text, row1
    This is bad text, row2
    ```

2. Use create-react-app to quickly create a Review UI with this template

    ``` npx create-react-app my-review --template mephisto-review ```

3. Build your react app

Change to the directory of your react app:

    cd my-review

Build your app

    npm run build

4. Run ```mephisto review```

    *Make note of the paths to your data file and react app*

    ``` $ cat ~/path/to/your/data.csv | mephisto review ~/path/to/your/my-review/build -o results.csv ```

5. Open the react app hosted at the port specified by the ouput from the above command

6. Review your sample data with the UI prompts

7. View your review results in the generated ``` results.csv ```
