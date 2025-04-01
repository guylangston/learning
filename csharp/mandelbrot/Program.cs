using System.Numerics;

public record LinearMap(double A0, double A1, double B0, double B1)
{
    public double InterpolateToA(double b)
    {
        if (b < B0 || b > B1) throw new InvalidDataException();
        var r = (b - B0) / (B1 - B0);

        return (A1 - A0)*r + A0;
    }
}

public class Mandelbrot
{
    public static int InerateZ(Complex c, double upperBound, int maxInterations)
    {
        var i=0;
        var z = new Complex(0,0);
        while(Math.Abs(z.Real) < upperBound && Math.Abs(z.Imaginary) < upperBound)
        {
            if (i > maxInterations) return -1;
            z = z*z + c;
            i++;
        }
        return i;
    }

    public static int[,] ComputeDiagram(LinearMap real, LinearMap imag, int maxInterations)
    {
        var buffer = new int[(int)(real.B1 - real.B0), (int)(imag.B1 - imag.B0)];
        for(int x=0; x<buffer.GetLength(0); x++)
        {
            for(int y=0; y<buffer.GetLength(1); y++)
            {
                buffer[x,y] = InerateZ(new Complex(real.InterpolateToA(x), imag.InterpolateToA(y)), 1_000, maxInterations);
            }
        }
        return buffer;
    }

    public static void RenderAsciiDiagram(TextWriter outp, string byIntensity, int[,] buffer)
    {
        for(int y=0; y<buffer.GetLength(1); y++)
        {
            for(int x=0; x<buffer.GetLength(0); x++)
            {
                var b = buffer[x,y];
                outp.Write(mapChar(b));
            }
            outp.WriteLine();
        }

        char mapChar(int i)
        {
            if (i < 0) return ' ';
            if (i >= byIntensity.Length) return '!';
            return byIntensity[i];
        }
    }
}

public static class Program
{
    public static void Main()
    {
        var byIntensity = "`.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@";
        var diagram = Mandelbrot.ComputeDiagram(new LinearMap(-2.2, 2, 0, 80), new LinearMap(-1.5, 1.5, 0, 40), byIntensity.Length);
        Mandelbrot.RenderAsciiDiagram(Console.Out, byIntensity, diagram);
    }
}
