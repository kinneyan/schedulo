const NotFoundPage = () =>
{
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center">
            <h1 className="text-6xl font-bold text-foreground">404</h1>
            <p className="text-muted-foreground">Page not found.</p>
            <a href="/" className="text-primary underline text-sm">Go home</a>
        </div>
    );
};

export default NotFoundPage;
