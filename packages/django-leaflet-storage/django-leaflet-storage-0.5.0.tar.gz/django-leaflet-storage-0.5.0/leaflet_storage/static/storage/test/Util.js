describe('L.Util', function () {

    describe('#toHTML()', function () {

        it('should handle bold', function () {
            assert.equal(L.Util.toHTML('Some **bold**'), 'Some <strong>bold</strong>');
        });

        it('should handle italic', function () {
            assert.equal(L.Util.toHTML('Some *italic*'), 'Some <em>italic</em>');
        });

        it('should handle links without formatting', function () {
            assert.equal(L.Util.toHTML('A simple http://osm.org link'), 'A simple <a target="_blank" href="http://osm.org">http://osm.org</a> link');
        });

        it('should handle simple link inside parenthesis', function () {
            assert.equal(L.Util.toHTML('A simple link (http://osm.org)'), 'A simple link (<a target="_blank" href="http://osm.org">http://osm.org</a>)');
        });

        it('should handle simple link with formatting', function () {
            assert.equal(L.Util.toHTML('A simple [[http://osm.org]] link'), 'A simple <a target="_blank" href="http://osm.org">http://osm.org</a> link');
        });

        it('should handle simple link with formatting and content', function () {
            assert.equal(L.Util.toHTML('A simple [[http://osm.org|link]]'), 'A simple <a target="_blank" href="http://osm.org">link</a>');
        });

        it('should handle image', function () {
            assert.equal(L.Util.toHTML('A simple image: {{http://osm.org/pouet.png}}'), 'A simple image: <img src="http://osm.org/pouet.png">');
        });

        it('should handle image with alt', function () {
            assert.equal(L.Util.toHTML('A simple image: {{http://osm.org/pouet.png|alt text}}'), 'A simple image: <img src="http://osm.org/pouet.png" alt="alt text">');
        });

    });

    describe('#escapeHTML', function () {

        it('should escape HTML tags', function () {
            assert.equal(L.Util.escapeHTML('<a href="pouet">'), '&lt;a href="pouet">');
        });

        it('should not fail with int value', function () {
            assert.equal(L.Util.escapeHTML(25), '25');
        });

        it('should not fail with null value', function () {
            assert.equal(L.Util.escapeHTML(null), '');
        });

    });

});