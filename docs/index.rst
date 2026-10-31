fresh-cbm
=========

Exact cached libcbm stand-state tables and lookup client for WS4/FEMIC carbon
analyses.

This site is the RTFM surface for the project. Agents read the relevant page
before they act and cite it in their reports. Start with the repository's
``AGENTS.md`` and ``ROADMAP.md``.

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/index

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/index

.. toctree::
   :maxdepth: 2
   :caption: Agents

   agents/index

.. toctree::
   :maxdepth: 2
   :caption: API

   api/index

RTFM map
--------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - If you need to
     - Read
   * - Understand why the package exists and who it serves
     - :doc:`guides/context`
   * - See a worked application
     - :doc:`guides/applications`
   * - Understand the cache contract
     - :doc:`guides/cache-format`
   * - Build or validate a cache
     - :doc:`guides/building`
   * - Release a cache
     - :doc:`guides/releasing`
   * - Use the Python client
     - :doc:`api/fresh-cbm`
   * - Change the package
     - ``AGENTS.md`` and :doc:`reference/validation`

Machine readers can start from ``llms.txt`` at the root of the published site.
