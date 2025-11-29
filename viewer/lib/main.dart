import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter/services.dart' show rootBundle;

void main() {
  runApp(const RecipeApp());
}

class Recipe {
  final String title;
  final String chapter;
  final int serves;
  final int duration;
  final List<String> ingredients;
  final List<String> steps;
  final List<String> images;
  String notes;

  Recipe({
    required this.title,
    required this.chapter,
    required this.serves,
    required this.duration,
    required this.ingredients,
    required this.steps,
    this.images = const [],
    this.notes = '',
  });

  factory Recipe.fromJson(Map<String, dynamic> json) => Recipe(
    title: json['Name'],
    chapter: json['Kapitel'],
    serves: json['Serves'],
    duration: json['Dauer'],
    ingredients: List<String>.from(json['Zutaten']),
    steps: List<String>.from(json['Anleitung']),
    images: json['Bild'] == null ? [] : List<String>.from(json['Bild']),
    notes: json['Notes'] ?? '',
  );
}

class RecipeApp extends StatelessWidget {
  const RecipeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('de'),
      ],
      home: RecipeHomePage(),
    );
  }
}

class RecipeHomePage extends StatefulWidget {
  @override
  State<RecipeHomePage> createState() => _RecipeHomePageState();
}

class _RecipeHomePageState extends State<RecipeHomePage> {
  List<Recipe> allRecipes = [];
  String query = '';

  @override
  void initState() {
    super.initState();
    loadRecipes();
  }

  Future<void> loadRecipes() async {
    final jsonString = await rootBundle.loadString('assets/recipes.json');
    final data = json.decode(jsonString);
    final docs = data['documents'] as List;
    setState(() {
      allRecipes = docs.map((e) => Recipe.fromJson(e)).toList();
      // Sort all recipes by name
      allRecipes.sort((a, b) => a.title.toLowerCase().compareTo(b.title.toLowerCase()));
    });
  }


  @override
  Widget build(BuildContext context) {
    List<Recipe> filtered = allRecipes
        .where((r) => r.title.toLowerCase().contains(query.toLowerCase()))
        .toList();

    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.appTitle),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: TextField(
              decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: AppLocalizations.of(context)!.searchHint
              ),
              onChanged: (value) {
                setState(() => query = value);
              },
            ),
          ),

          Expanded(
            child: ListView.builder(
              itemCount: filtered.length,
              itemBuilder: (context, index) {
                final recipe = filtered[index];
                return ListTile(
                  title: Text(recipe.title),
                  subtitle: Text('${recipe.chapter} · ${recipe.duration} min'),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => RecipeDetailPage(recipe: recipe),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class RecipeDetailPage extends StatefulWidget {
  final Recipe recipe;

  const RecipeDetailPage({super.key, required this.recipe});

  @override
  State<RecipeDetailPage> createState() => _RecipeDetailPageState();
}

class _RecipeDetailPageState extends State<RecipeDetailPage> {
  late TextEditingController _notesController;

  @override
  void initState() {
    super.initState();
    _notesController = TextEditingController(text: widget.recipe.notes);
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.recipe.title),
          bottom: TabBar(tabs: [
            Tab(text: AppLocalizations.of(context)!.ingredientsTab),
            Tab(text: AppLocalizations.of(context)!.stepsTab),
          ]),
        ),
        body: TabBarView(
          children: [
            ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text('${AppLocalizations.of(context)!.serves}: ${widget.recipe.serves}'),
                Text('${AppLocalizations.of(context)!.duration}: ${widget.recipe.duration} ${AppLocalizations.of(context)!.minutes}'),
                const SizedBox(height: 12),
                ...widget.recipe.ingredients
                    .map((i) => Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Text('- $i'),
                ))
                    .toList(),
              ],
            ),

            ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // Display each step
                ...widget.recipe.steps.map((s) => Padding(
                  padding: const EdgeInsets.only(bottom: 12.0),
                  child: Text('• $s'),
                )),

                // Add some spacing before notes
                const SizedBox(height: 16),

                const SizedBox(height: 16),

                // Editable notes
                Text(AppLocalizations.of(context)!.notes, style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                TextField(
                  controller: _notesController,
                  maxLines: null,
                  decoration: InputDecoration(
                    border: OutlineInputBorder(),
                    hintText: 'Add your own notes here...',
                  ),
                  onChanged: (value) {
                    // Update the recipe object in memory
                    widget.recipe.notes = value;
                  },
                ),
              ],
            )

          ],
        ),
      ),
    );
  }
}
