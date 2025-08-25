"use client"

const SectionSelector = ({ sections, activeSection, setActiveSection }) => {
  return (
    <div className="bg-white rounded-xl shadow-md mb-6 overflow-hidden">
      <div className="p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Class Sections</h2>
        <div className="flex flex-wrap gap-2">
          {sections.map((section) => (
            <button
              key={section}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === section ? "bg-purple-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
              onClick={() => setActiveSection(section)}
            >
              {section}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default SectionSelector
