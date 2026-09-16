import Link from "next/link";

const links = [
  ["/", "Home"],
  ["/results/experimental/", "Experimental Results"],
  ["/results/manual-validation/", "Manual Validation"],
  ["/results/coleus-109/", "Coleus 109"],
] as const;

export default function ResultsNavigation({ current }: { current: string }) {
  return (
    <nav aria-label="Results navigation" className="border-b border-green-900/40 bg-[#07100c]/95">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-2 px-6 py-4">
        <span className="mr-2 text-xs font-semibold uppercase tracking-widest text-green-100/45">Navigate</span>
        {links.map(([href, label]) => {
          const active = current === href;
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
                active
                  ? "border-lime-300 bg-lime-300 text-[#04100a]"
                  : "border-green-700/40 text-green-100/75 hover:border-lime-300/60 hover:text-lime-200"
              }`}
            >
              {label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
