

arg_handler support is somewhere in ../aaargh.new/. Relevant part for the
tests::

    app.arg('--spam', default='SPAM')

    @app.arg_handler
    def spam_remover(d):
        d.pop('spam', None)

