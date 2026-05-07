using VoltPy.Service;

var app = args.FirstOrDefault(arg => !arg.StartsWith("--", StringComparison.Ordinal)) ?? "example_app";
var devFallback = args.Contains("--dev-python-fallback", StringComparer.OrdinalIgnoreCase);
var supervise = args.Contains("--supervise", StringComparer.OrdinalIgnoreCase);

using var cts = new CancellationTokenSource();
Console.CancelKeyPress += (_, eventArgs) =>
{
    eventArgs.Cancel = true;
    cts.Cancel();
};

try
{
    var service = VoltPyService.Create(devFallback);
    return supervise
        ? await service.RunSupervisorAsync(app, TimeSpan.FromSeconds(5), cts.Token)
        : await service.RunOnceAsync(app, cts.Token);
}
catch (Exception ex)
{
    Console.Error.WriteLine(ex);
    return 1;
}
