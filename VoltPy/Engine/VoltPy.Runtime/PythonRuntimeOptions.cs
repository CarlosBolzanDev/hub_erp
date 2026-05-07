namespace VoltPy.Runtime;

public sealed record PythonRuntimeOptions
{
    public bool HiddenWindow { get; init; } = true;
    public bool UseSystemPythonFallback { get; init; } = false;
    public IReadOnlyList<string> AdditionalPythonPath { get; init; } = Array.Empty<string>();
}
