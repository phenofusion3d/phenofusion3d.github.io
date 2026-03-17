"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import Image from "next/image";
import { Mail } from "lucide-react";

const teamLead = {
  name: "Saswat Panda",
  role: "Team Lead",
  email: "Saswat.panda@anu.edu.au",
  avatar: "https://avatars.githubusercontent.com/u/45821961?v=4",
  bio: "Saswat Panda leads the PhenoFusion3D project at APPN ANU, guiding the overall project direction and supporting the team's technical and research goals.",
};

const projectLeadership = [
  {
    name: "Supriyo Shafkat Ahmed",
    role: "Data Lead",
    email: "SUPRIYOSHAFKAT.AHMED@anu.edu.au",
    bio: "Supriyo supports the project as Data Lead, contributing to data-related planning, organisation, and technical guidance for the team.",
  },
];

const studentMembers = [
  { name: "Adithya Rama",   role: "Student at ANU", email: "Adithya.Rama@anu.edu.au" },
  { name: "Tanisha Sharma", role: "Student at ANU", email: "Tanisha.Sharma@anu.edu.au" },
  { name: "Howard Zhang",   role: "Student at ANU", email: "u7877905@anu.edu.au" },
  { name: "Tianyu Xu",      role: "Student at ANU", email: "Tianyu.Xu@anu.edu.au" },
  // { name: "Flynn Nyhof",    role: "Student at ANU", email: "u7650207@anu.edu.au" },
];

function getInitials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export default function Team() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="team" ref={ref} className="relative py-28 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#050a0a] via-[#071510] to-[#050a0a]" />
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-green-500/30 to-transparent" />
      <div className="absolute top-1/2 right-0 w-[500px] h-[500px] rounded-full bg-green-500/3 blur-[120px] -translate-y-1/2" />

      <div className="relative z-10 max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-green-500/30 bg-green-500/10 text-green-400 text-xs font-semibold uppercase tracking-widest mb-6"
          >
            Meet the Team
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-5xl font-black text-white mb-4"
          >
            Built by{" "}
            <span className="bg-gradient-to-r from-green-400 to-lime-400 bg-clip-text text-transparent">
              Researchers & Students
            </span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-green-100/50 max-w-xl mx-auto text-base"
          >
            PhenoFusion3D is supported by APPN ANU and developed collaboratively with guidance from the
            project leadership team and contributions from student members at ANU.
          </motion.p>
        </div>

        {/* Team Lead */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="mb-8 p-8 rounded-2xl border border-green-500/25 bg-gradient-to-br from-[#0f1f15] to-[#0a1510] flex flex-col sm:flex-row items-center sm:items-start gap-6"
        >
          {/* Avatar */}
          <div className="flex-shrink-0 relative">
            <div className="w-28 h-28 rounded-full overflow-hidden border-4 border-green-500/40 shadow-xl shadow-green-950/50">
              <Image
                src={teamLead.avatar}
                alt={teamLead.name}
                width={112}
                height={112}
                className="object-cover w-full h-full"
                unoptimized
              />
            </div>
            <div className="absolute -bottom-1 -right-1 w-7 h-7 rounded-full bg-gradient-to-br from-green-400 to-lime-500 border-2 border-[#0a1510] flex items-center justify-center">
              <span className="text-[10px]">⭐</span>
            </div>
          </div>

          {/* Info */}
          <div className="flex-1 text-center sm:text-left">
            <span className="inline-block px-3 py-1 rounded-full bg-green-500/15 border border-green-500/30 text-green-300 text-xs font-bold uppercase tracking-widest mb-3">
              {teamLead.role}
            </span>
            <h3 className="text-white text-2xl font-black mb-2">{teamLead.name}</h3>
            <a
              href={`mailto:${teamLead.email}`}
              className="inline-flex items-center gap-1.5 text-green-400 text-sm font-semibold hover:text-green-300 transition mb-3"
            >
              <Mail className="w-3.5 h-3.5" />
              {teamLead.email}
            </a>
            <p className="text-green-100/55 text-sm leading-relaxed">{teamLead.bio}</p>
          </div>
        </motion.div>

        {/* Project Leadership */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.35 }}
          className="mb-8 rounded-2xl border border-green-500/20 bg-gradient-to-br from-[#0f1f15] to-[#0a1510] overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-green-900/30 bg-[#0d1a12]">
            <div className="text-xs font-bold text-green-400/70 uppercase tracking-wider">Project Leadership</div>
          </div>
          <div className="p-6 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {projectLeadership.map((member, i) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.4 + i * 0.1 }}
                whileHover={{ y: -4, scale: 1.02 }}
                className="p-4 rounded-xl border border-green-500/15 bg-[#0a1510] hover:border-green-500/30 transition-all duration-300"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-lime-500/30 to-green-500/20 border border-lime-500/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-lime-300 text-xs font-bold">{getInitials(member.name)}</span>
                  </div>
                  <div>
                    <div className="text-white font-bold text-sm leading-snug">{member.name}</div>
                    <span className="inline-block px-2 py-0.5 rounded-full bg-lime-500/10 border border-lime-500/25 text-lime-400 text-[10px] font-semibold mt-0.5">
                      {member.role}
                    </span>
                  </div>
                </div>
                <p className="text-green-100/45 text-xs leading-relaxed mb-2">{member.bio}</p>
                <a
                  href={`mailto:${member.email}`}
                  className="inline-flex items-center gap-1 text-green-400/70 text-xs hover:text-green-300 transition"
                >
                  <Mail className="w-3 h-3" />
                  {member.email}
                </a>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Student Team Members */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="rounded-2xl border border-green-500/20 bg-gradient-to-br from-[#0f1f15] to-[#0a1510] overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-green-900/30 bg-[#0d1a12]">
            <div className="text-xs font-bold text-green-400/70 uppercase tracking-wider">Student Team Members · ANU</div>
          </div>
          <div className="p-6 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {studentMembers.map((member, i) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.55 + i * 0.08 }}
                whileHover={{ y: -4, scale: 1.02 }}
                className="p-4 rounded-xl border border-green-500/15 bg-[#0a1510] hover:border-green-500/30 transition-all duration-300"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-green-500/25 to-emerald-500/15 border border-green-500/25 flex items-center justify-center flex-shrink-0">
                    <span className="text-green-300 text-xs font-bold">{getInitials(member.name)}</span>
                  </div>
                  <div>
                    <div className="text-white font-semibold text-sm leading-snug">{member.name}</div>
                    <div className="text-green-100/40 text-xs">{member.role}</div>
                  </div>
                </div>
                <a
                  href={`mailto:${member.email}`}
                  className="inline-flex items-center gap-1 text-green-400/60 text-xs hover:text-green-300 transition"
                >
                  <Mail className="w-3 h-3" />
                  {member.email}
                </a>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
