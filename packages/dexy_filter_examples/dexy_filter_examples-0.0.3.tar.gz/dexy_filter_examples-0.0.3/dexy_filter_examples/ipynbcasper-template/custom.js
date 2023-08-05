// Script template - will have string interpolation applied.

casper.test.begin('notebook-list', 1, function suite(test) {
    casper.start("http://localhost:%(port)s", function() {
        this.waitForSelector("#notebook_list");
    });

    casper.then(function() {
        test.assertSelectorHasText("span.item_name", "Trapezoid Rule");
        this.capture('%(name)s-notebook-list%(ext)s');
        console.log("Finished running script.");
    });

    casper.run(function() {
        test.done();
    });
});

