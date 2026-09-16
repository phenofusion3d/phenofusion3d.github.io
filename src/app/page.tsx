import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import About from "@/components/About";
import Features from "@/components/Features";
import Pipeline from "@/components/Pipeline";
import Visualisation from "@/components/Visualisation";
import Results from "@/components/Results";
import TechStack from "@/components/TechStack";
import Organisation from "@/components/Organisation";
import Team from "@/components/Team";
import Contact from "@/components/Contact";

export default function Home() {
  return (
    <main className="relative">
      <Navbar />
      <Hero />
      <About />
      <Features />
      <Pipeline />
      <Visualisation />
      <section className="mx-auto max-w-7xl px-6 py-8">
        <p className="text-xs font-semibold uppercase tracking-widest text-lime-400">Current research outputs</p>
        <h2 className="mt-3 text-3xl font-semibold text-white">Explore reconstruction, validation and fusion results</h2>
        <div className="mt-6 grid gap-5 lg:grid-cols-3">
          <a href={`${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/results/experimental/`} className="group block rounded-xl border border-cyan-300/30 bg-cyan-950/20 p-6 transition hover:border-cyan-300/55 hover:bg-cyan-950/35">
            <p className="text-xs font-semibold uppercase tracking-widest text-cyan-300">Experimental results</p>
            <h3 className="mt-2 text-2xl font-semibold text-white">Hyperspectral and RGB-D fusion →</h3>
            <p className="mt-3 leading-7 text-green-100/65">Inspect 10,485 measured spectral 3D points, 427 wavelength bands and candidate placement in the legacy ICP scene.</p>
            <div className="mt-5 space-y-2 text-sm">
              <p className="rounded-lg bg-black/20 px-3 py-2 text-cyan-100"><span className="font-semibold text-cyan-300">Hyperspectral:</span> 20260828</p>
              <p className="break-all rounded-lg bg-black/20 px-3 py-2 text-cyan-100"><span className="font-semibold text-cyan-300">RGB-D:</span> test_plant_20260828120800_best_lighting</p>
            </div>
          </a>
          <a href={`${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/results/manual-validation/`} className="group block rounded-xl border border-amber-300/30 bg-amber-950/20 p-6 transition hover:border-amber-300/55 hover:bg-amber-950/35">
            <p className="text-xs font-semibold uppercase tracking-widest text-amber-300">Manual validation</p>
            <h3 className="mt-2 text-2xl font-semibold text-white">Manual versus software traits →</h3>
            <p className="mt-3 leading-7 text-green-100/65">Review all three plant-height comparisons and nine matched-leaf length and width measurements with audit images.</p>
            <p className="mt-5 break-all rounded-lg bg-black/20 px-3 py-2 text-sm text-amber-100"><span className="font-semibold text-amber-300">Dataset:</span> test_plant_20260828120800_best_lighting</p>
          </a>
          <a href={`${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/results/coleus-109/`} className="group block rounded-xl border border-lime-400/30 bg-green-950/40 p-6 transition hover:border-lime-400/55 hover:bg-green-900/40">
            <p className="text-xs font-semibold uppercase tracking-widest text-lime-400">Reconstruction study</p>
            <h3 className="mt-2 text-2xl font-semibold text-white">Explore the recovered Coleus 109 →</h3>
            <p className="mt-3 leading-7 text-green-100/65">The complete interactive comparison, downloadable model, remaining gaps and a practical plan for better capture.</p>
            <p className="mt-5 rounded-lg bg-black/20 px-3 py-2 text-sm text-lime-100"><span className="font-semibold text-lime-300">Dataset:</span> 20260901122109</p>
          </a>
        </div>
      </section>
      <Results />
      <TechStack />
      <Organisation />
      <Team />
      <Contact />
    </main>
  );
}
